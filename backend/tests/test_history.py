from pathlib import Path

from labelverify.contracts.models import AnalysisDraft
from labelverify.persistence.history import HISTORY_LIMIT, HistoryRepository

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
