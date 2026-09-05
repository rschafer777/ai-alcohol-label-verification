import sqlite3
from pathlib import Path

import pytest
from labelverify.contracts.models import AnalysisDraft
from labelverify.persistence.history import (
    HISTORY_LIMIT,
    REVISION_LIMIT,
    HistoryRepository,
    RevisionConflict,
    RevisionLimit,
)

from .helpers import fake_result, reference

SCOPE_A = "a" * 43
SCOPE_B = "b" * 43


def test_history_round_trip_disposition_and_delete(tmp_path: Path) -> None:
    repository = HistoryRepository(tmp_path / "history")
    repository.initialize()
    panel = tmp_path / "panel.png"
    panel.write_bytes(b"test-image")

    record_id = repository.add(reference(), fake_result("history-one"), (panel,), scope_id=SCOPE_A)

    listing = repository.list(scope_id=SCOPE_A)
    assert listing["total"] == 1
    assert listing["cap"] == HISTORY_LIMIT
    detail = repository.get(record_id, scope_id=SCOPE_A)
    assert detail is not None
    assert detail["requestId"] == "history-one"
    assert repository.panel_path(record_id, "panel-1", scope_id=SCOPE_A) is not None

    assert repository.update_disposition(record_id, "approved", "Reviewed", scope_id=SCOPE_A)
    updated = repository.get(record_id, scope_id=SCOPE_A)
    assert updated is not None
    assert updated["disposition"] == "approved"
    assert updated["reviewerNote"] == "Reviewed"

    assert repository.delete(record_id, scope_id=SCOPE_A)
    assert repository.get(record_id, scope_id=SCOPE_A) is None
    assert repository.panel_path(record_id, "panel-1", scope_id=SCOPE_A) is None


def test_history_scope_isolates_read_write_and_delete(tmp_path: Path) -> None:
    repository = HistoryRepository(tmp_path / "history")
    repository.initialize()
    panel = tmp_path / "panel.png"
    panel.write_bytes(b"test-image")
    record_id = repository.add(
        reference(), fake_result("history-private"), (panel,), scope_id=SCOPE_A
    )

    assert repository.list(scope_id=SCOPE_B)["total"] == 0
    assert repository.get(record_id, scope_id=SCOPE_B) is None
    assert repository.panel_path(record_id, "panel-1", scope_id=SCOPE_B) is None
    assert not repository.update_disposition(record_id, "approved", "not allowed", scope_id=SCOPE_B)
    assert not repository.delete(record_id, scope_id=SCOPE_B)
    assert repository.clear(scope_id=SCOPE_B) == 0
    assert repository.get(record_id, scope_id=SCOPE_A) is not None


def test_lineage_delete_failure_rolls_back_before_blob_unlink(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repository = HistoryRepository(tmp_path / "history")
    repository.initialize()
    panel = tmp_path / "panel.png"
    panel.write_bytes(b"test-image")
    record_id = repository.add(
        reference(), fake_result("history-delete-failure"), (panel,), scope_id=SCOPE_A
    )
    blob = repository.panel_path(record_id, "panel-1", scope_id=SCOPE_A)
    assert blob is not None and blob.is_file()
    delete_lineage = repository._delete_lineage

    def fail_before_commit(connection: sqlite3.Connection, root_id: str) -> list[Path]:
        delete_lineage(connection, root_id)
        raise sqlite3.OperationalError("injected transaction failure")

    monkeypatch.setattr(repository, "_delete_lineage", fail_before_commit)
    with pytest.raises(sqlite3.OperationalError, match="injected"):
        repository.delete(record_id, scope_id=SCOPE_A)

    assert repository.get(record_id, scope_id=SCOPE_A) is not None
    assert blob.is_file()


def test_history_retains_unresolved_analysis_for_human_review(tmp_path: Path) -> None:
    repository = HistoryRepository(tmp_path / "history")
    repository.initialize()
    panel = tmp_path / "panel.png"
    panel.write_bytes(b"test-image")
    draft = AnalysisDraft(
        beverageType=None,
        brandName="CLOUD NINE",
        classType="Hard Seltzer",
        isImported=False,
    )

    record_id = repository.add(
        draft,
        fake_result("history-unresolved"),
        (panel,),
        scope_id=SCOPE_A,
    )

    detail = repository.get(record_id, scope_id=SCOPE_A)
    assert detail is not None
    assert detail["beverageType"] == "unresolved"
    assert detail["displayName"] == "CLOUD NINE"


def test_history_enforces_fifo_cap(tmp_path: Path) -> None:
    repository = HistoryRepository(tmp_path / "history")
    repository.initialize()
    panel = tmp_path / "panel.png"
    panel.write_bytes(b"test-image")
    first_id = ""

    for ordinal in range(HISTORY_LIMIT + 1):
        record_id = repository.add(
            reference(brand=f"PRODUCT {ordinal:03d}"),
            fake_result(f"history-{ordinal:03d}"),
            (panel,),
            scope_id=SCOPE_A,
        )
        if ordinal == 0:
            first_id = record_id

    listing = repository.list(scope_id=SCOPE_A, page_size=HISTORY_LIMIT)
    assert listing["total"] == HISTORY_LIMIT
    assert repository.get(first_id, scope_id=SCOPE_A) is None
    assert not (repository.images / first_id).exists()


def test_history_fifo_cap_is_global_across_rotated_scopes(tmp_path: Path) -> None:
    repository = HistoryRepository(tmp_path / "history")
    repository.initialize()
    panel = tmp_path / "panel.png"
    panel.write_bytes(b"test-image")
    first_id = ""

    for ordinal in range(HISTORY_LIMIT + 1):
        scope = SCOPE_A if ordinal % 2 == 0 else SCOPE_B
        record_id = repository.add(
            reference(brand=f"ROTATED {ordinal:03d}"),
            fake_result(f"rotated-{ordinal:03d}"),
            (panel,),
            scope_id=scope,
        )
        if ordinal == 0:
            first_id = record_id

    with sqlite3.connect(repository.database) as connection:
        retained = connection.execute("SELECT COUNT(*) FROM history_lineages").fetchone()[0]
    assert retained == HISTORY_LIMIT
    assert repository.get(first_id, scope_id=SCOPE_A) is None
    assert repository.list(scope_id=SCOPE_A)["total"] == HISTORY_LIMIT // 2
    assert repository.list(scope_id=SCOPE_B)["total"] == HISTORY_LIMIT // 2


def test_history_revisions_share_blobs_and_delete_as_one_lineage(tmp_path: Path) -> None:
    repository = HistoryRepository(tmp_path / "history")
    repository.initialize()
    panel = tmp_path / "panel.png"
    panel.write_bytes(b"test-image")
    original = fake_result("revision-one")
    first_id = repository.add(reference(), original, (panel,), scope_id=SCOPE_A)
    revised = fake_result("revision-two").model_copy(update={"revision_kind": "correction"})

    second_id, revision, root_id = repository.add_revision(
        reference(brand="OLD TOM CORRECTED"),
        revised,
        (panel,),
        record_id=first_id,
        expected_revision=1,
        revision_kind="correction",
        scope_id=SCOPE_A,
        corrections=[{"field": "brand_name", "visibleText": "OLD TOM CORRECTED"}],
    )

    assert revision == 2
    assert root_id == first_id
    assert repository.list(scope_id=SCOPE_A)["total"] == 1
    old = repository.get(first_id, scope_id=SCOPE_A)
    current = repository.get(second_id, scope_id=SCOPE_A)
    assert old is not None and current is not None
    assert old["isLatest"] is False
    assert current["isLatest"] is True
    assert len(current["revisions"]) == 2
    with sqlite3.connect(repository.database) as connection:
        assert connection.execute("SELECT COUNT(*) FROM image_blobs").fetchone()[0] == 1
        assert connection.execute("SELECT ref_count FROM image_blobs").fetchone()[0] == 2

    assert repository.delete(first_id, scope_id=SCOPE_A)
    assert repository.get(second_id, scope_id=SCOPE_A) is None
    with sqlite3.connect(repository.database) as connection:
        assert connection.execute("SELECT COUNT(*) FROM image_blobs").fetchone()[0] == 0


def test_history_revision_compare_and_swap_and_cap(tmp_path: Path) -> None:
    repository = HistoryRepository(tmp_path / "history")
    repository.initialize()
    panel = tmp_path / "panel.png"
    panel.write_bytes(b"test-image")
    current_id = repository.add(
        reference(), fake_result("revision-cap-1"), (panel,), scope_id=SCOPE_A
    )

    second_id, _, _ = repository.add_revision(
        reference(brand="REVISION 2"),
        fake_result("revision-cap-2"),
        (panel,),
        record_id=current_id,
        expected_revision=1,
        revision_kind="correction",
        scope_id=SCOPE_A,
    )
    with pytest.raises(RevisionConflict):
        repository.add_revision(
            reference(brand="STALE"),
            fake_result("revision-stale"),
            (panel,),
            record_id=current_id,
            expected_revision=1,
            revision_kind="correction",
            scope_id=SCOPE_A,
        )

    current_id = second_id
    for expected in range(2, REVISION_LIMIT):
        current_id, revision, _ = repository.add_revision(
            reference(brand=f"REVISION {expected + 1}"),
            fake_result(f"revision-cap-{expected + 1}"),
            (panel,),
            record_id=current_id,
            expected_revision=expected,
            revision_kind="correction",
            scope_id=SCOPE_A,
        )
        assert revision == expected + 1
    with pytest.raises(RevisionLimit):
        repository.add_revision(
            reference(brand="REVISION 11"),
            fake_result("revision-cap-11"),
            (panel,),
            record_id=current_id,
            expected_revision=REVISION_LIMIT,
            revision_kind="correction",
            scope_id=SCOPE_A,
        )


def test_history_revision_does_not_reset_fifo_age(tmp_path: Path) -> None:
    repository = HistoryRepository(tmp_path / "history")
    repository.initialize()
    panel = tmp_path / "panel.png"
    panel.write_bytes(b"test-image")
    first_id = repository.add(
        reference(), fake_result("revision-age-1"), (panel,), scope_id=SCOPE_A
    )
    with sqlite3.connect(repository.database) as connection:
        before = connection.execute(
            "SELECT root_created_at FROM history_lineages WHERE root_id = ?", (first_id,)
        ).fetchone()[0]
    second_id, _, _ = repository.add_revision(
        reference(brand="CORRECTED"),
        fake_result("revision-age-2"),
        (panel,),
        record_id=first_id,
        expected_revision=1,
        revision_kind="correction",
        scope_id=SCOPE_A,
    )
    with sqlite3.connect(repository.database) as connection:
        after = connection.execute(
            "SELECT root_created_at FROM history_lineages WHERE root_id = ?", (first_id,)
        ).fetchone()[0]
    assert after == before
    assert repository.list(scope_id=SCOPE_A)["items"][0]["id"] == second_id
