from __future__ import annotations

import builtins
import json
import shutil
import sqlite3
import threading
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from uuid import uuid4

from labelverify.contracts.models import AnalysisDraft, ReferenceRecord, VerificationResult
from labelverify.security.signatures import image_media_type

HISTORY_LIMIT = 500
REVISION_LIMIT = 10


class RevisionConflict(RuntimeError):
    pass


class RevisionLimit(RuntimeError):
    pass


class CorrectionUnavailable(RuntimeError):
    pass


class HistoryRepository:
    """SQLite product lineages, immutable revisions, and content-addressed evidence."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.database = root / "labelverify.sqlite3"
        self.images = root / "images"
        self.blobs = self.images / "blobs"
        self._lock = threading.RLock()

    def initialize(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.blobs.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.executescript(
                """
                PRAGMA foreign_keys = ON;
                CREATE TABLE IF NOT EXISTS history_lineages (
                    root_id TEXT PRIMARY KEY,
                    scope_id TEXT NOT NULL,
                    root_created_at TEXT NOT NULL,
                    latest_record_id TEXT NOT NULL,
                    latest_revision INTEGER NOT NULL,
                    display_name TEXT NOT NULL,
                    beverage_type TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    disposition TEXT,
                    reviewer_note TEXT NOT NULL DEFAULT ''
                );
                CREATE TABLE IF NOT EXISTS history_revisions (
                    id TEXT PRIMARY KEY,
                    root_id TEXT NOT NULL REFERENCES history_lineages(root_id) ON DELETE CASCADE,
                    revision INTEGER NOT NULL,
                    revision_kind TEXT NOT NULL,
                    parent_id TEXT,
                    created_at TEXT NOT NULL,
                    request_id TEXT NOT NULL UNIQUE,
                    reference_json TEXT NOT NULL,
                    result_json TEXT NOT NULL,
                    observation_json TEXT,
                    corrections_json TEXT NOT NULL DEFAULT '[]',
                    correction_event_json TEXT,
                    disposition TEXT,
                    reviewer_note TEXT NOT NULL DEFAULT '',
                    UNIQUE(root_id, revision)
                );
                CREATE TABLE IF NOT EXISTS image_blobs (
                    sha256 TEXT PRIMARY KEY,
                    relative_path TEXT NOT NULL UNIQUE,
                    media_type TEXT NOT NULL,
                    byte_count INTEGER NOT NULL,
                    ref_count INTEGER NOT NULL CHECK(ref_count >= 0)
                );
                CREATE TABLE IF NOT EXISTS revision_panels (
                    record_id TEXT NOT NULL REFERENCES history_revisions(id) ON DELETE CASCADE,
                    panel_id TEXT NOT NULL,
                    ordinal INTEGER NOT NULL,
                    blob_sha256 TEXT NOT NULL REFERENCES image_blobs(sha256),
                    original_name TEXT NOT NULL,
                    PRIMARY KEY(record_id, panel_id)
                );
                CREATE INDEX IF NOT EXISTS lineages_scope_created
                ON history_lineages(scope_id, root_created_at DESC, root_id DESC);
                CREATE INDEX IF NOT EXISTS revisions_root_revision
                ON history_revisions(root_id, revision DESC);
                """
            )
            self._migrate_legacy(connection)
        self._cleanup_orphan_files()

    def add(
        self,
        reference: ReferenceRecord | AnalysisDraft,
        result: VerificationResult,
        panel_paths: tuple[Path, ...],
        *,
        scope_id: str,
    ) -> str:
        record_id = f"hist_{uuid4().hex}"
        created_at = datetime.now(UTC).isoformat()
        display_name, beverage_type = self._display_values(reference)
        stored_result = result.model_copy(
            update={
                "history_id": record_id,
                "root_id": record_id,
                "parent_id": None,
                "revision": 1,
                "revision_kind": "original",
            }
        )
        orphan_paths: builtins.list[Path] = []
        with self._lock, self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            connection.execute(
                """
                INSERT INTO history_lineages (
                    root_id, scope_id, root_created_at, latest_record_id, latest_revision,
                    display_name, beverage_type, summary
                ) VALUES (?, ?, ?, ?, 1, ?, ?, ?)
                """,
                (
                    record_id,
                    scope_id,
                    created_at,
                    record_id,
                    display_name,
                    beverage_type,
                    stored_result.summary,
                ),
            )
            self._insert_revision(
                connection,
                record_id=record_id,
                root_id=record_id,
                revision=1,
                revision_kind="original",
                parent_id=None,
                created_at=created_at,
                reference=reference,
                result=stored_result,
                observation=result.observation_snapshot,
                corrections=[],
                correction_event=None,
                panel_paths=panel_paths,
            )
            orphan_paths = self._evict(connection)
        self._unlink_after_commit(orphan_paths)
        return record_id

    def add_revision(
        self,
        reference: ReferenceRecord | AnalysisDraft,
        result: VerificationResult,
        panel_paths: tuple[Path, ...],
        *,
        record_id: str,
        expected_revision: int,
        revision_kind: str,
        scope_id: str,
        corrections: list[dict[str, object]] | None = None,
        correction_event: dict[str, object] | None = None,
    ) -> tuple[str, int, str]:
        new_id = f"hist_{uuid4().hex}"
        created_at = datetime.now(UTC).isoformat()
        display_name, beverage_type = self._display_values(reference)
        with self._lock, self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                """
                SELECT l.root_id, l.latest_record_id, l.latest_revision
                FROM history_lineages l
                JOIN history_revisions r ON r.root_id = l.root_id
                WHERE r.id = ? AND l.scope_id = ?
                """,
                (record_id, scope_id),
            ).fetchone()
            if row is None:
                raise KeyError(record_id)
            root_id = str(row[0])
            parent_id = str(row[1])
            current_revision = int(row[2])
            if expected_revision != current_revision or record_id != parent_id:
                raise RevisionConflict(parent_id)
            if current_revision >= REVISION_LIMIT:
                raise RevisionLimit(root_id)
            revision = current_revision + 1
            stored_result = result.model_copy(
                update={
                    "history_id": new_id,
                    "root_id": root_id,
                    "parent_id": parent_id,
                    "revision": revision,
                    "revision_kind": revision_kind,
                }
            )
            self._insert_revision(
                connection,
                record_id=new_id,
                root_id=root_id,
                revision=revision,
                revision_kind=revision_kind,
                parent_id=parent_id,
                created_at=created_at,
                reference=reference,
                result=stored_result,
                observation=result.observation_snapshot,
                corrections=corrections or [],
                correction_event=correction_event,
                panel_paths=panel_paths,
            )
            connection.execute(
                """
                UPDATE history_lineages
                SET latest_record_id = ?, latest_revision = ?, display_name = ?,
                    beverage_type = ?, summary = ?, disposition = NULL, reviewer_note = ''
                WHERE root_id = ?
                """,
                (
                    new_id,
                    revision,
                    display_name,
                    beverage_type,
                    stored_result.summary,
                    root_id,
                ),
            )
        return new_id, revision, root_id

    def list(
        self,
        *,
        scope_id: str,
        beverage_type: str | None = None,
        summary: str | None = None,
        disposition: str | None = None,
        query: str | None = None,
        offset: int = 0,
        page_size: int = 25,
    ) -> dict[str, object]:
        clauses = ["l.scope_id = ?"]
        values: list[object] = [scope_id]
        if beverage_type:
            clauses.append("l.beverage_type = ?")
            values.append(beverage_type)
        if summary:
            clauses.append("l.summary = ?")
            values.append(summary)
        if disposition:
            clauses.append("l.disposition = ?")
            values.append(disposition)
        if query:
            clauses.append(
                "(l.display_name LIKE ? OR r.request_id LIKE ? OR l.reviewer_note LIKE ?)"
            )
            pattern = f"%{query}%"
            values.extend([pattern, pattern, pattern])
        where = " AND ".join(clauses)
        with self._lock, self._connect() as connection:
            total = int(
                connection.execute(
                    f"""SELECT COUNT(*) FROM history_lineages l
                    JOIN history_revisions r ON r.id = l.latest_record_id
                    WHERE {where}""",
                    values,
                ).fetchone()[0]
            )
            rows = connection.execute(
                f"""
                SELECT l.root_id, r.created_at, r.request_id, l.display_name,
                       l.beverage_type, l.summary, l.disposition, l.reviewer_note,
                       l.latest_record_id, l.latest_revision, r.revision_kind
                FROM history_lineages l
                JOIN history_revisions r ON r.id = l.latest_record_id
                WHERE {where}
                ORDER BY l.root_created_at DESC, l.root_id DESC
                LIMIT ? OFFSET ?
                """,
                [*values, page_size, offset],
            ).fetchall()
            items = [self._summary(connection, row) for row in rows]
        return {
            "items": items,
            "total": total,
            "cap": HISTORY_LIMIT,
            "offset": offset,
            "pageSize": page_size,
            "hasMore": offset + len(items) < total,
        }

    def get(
        self, record_id: str, *, scope_id: str, include_internal: bool = False
    ) -> dict[str, object] | None:
        with self._lock, self._connect() as connection:
            row = connection.execute(
                """
                SELECT r.id, r.created_at, r.request_id, l.display_name,
                       l.beverage_type, l.summary, r.disposition, r.reviewer_note,
                       l.root_id, r.revision, r.revision_kind, r.parent_id,
                       r.reference_json, r.result_json, r.observation_json,
                       r.corrections_json, r.correction_event_json,
                       l.latest_record_id, l.latest_revision
                FROM history_revisions r
                JOIN history_lineages l ON l.root_id = r.root_id
                WHERE r.id = ? AND l.scope_id = ?
                """,
                (record_id, scope_id),
            ).fetchone()
            if row is None:
                return None
            panels = self._panels(connection, record_id)
            revisions = [
                {
                    "id": item[0],
                    "revision": item[1],
                    "revisionKind": item[2],
                    "createdAt": item[3],
                    "isLatest": item[0] == row[17],
                }
                for item in connection.execute(
                    """SELECT id, revision, revision_kind, created_at
                    FROM history_revisions WHERE root_id = ? ORDER BY revision""",
                    (row[8],),
                ).fetchall()
            ]
        reference_value = json.loads(row[12])
        result_value = json.loads(row[13])
        revision_display = (
            reference_value.get("caseLabel")
            or reference_value.get("brandName")
            or row[3]
        )
        revision_type = reference_value.get("beverageType") or row[4]
        value: dict[str, object] = {
            "id": row[0],
            "createdAt": row[1],
            "requestId": row[2],
            "displayName": revision_display,
            "beverageType": revision_type,
            "summary": result_value.get("summary", row[5]),
            "disposition": row[6],
            "reviewerNote": row[7],
            "panelCount": len(panels),
            "panels": panels,
            "rootId": row[8],
            "revision": row[9],
            "revisionKind": row[10],
            "parentId": row[11],
            "isLatest": row[0] == row[17],
            "latestRevision": row[18],
            "correctionAvailable": row[14] is not None,
            "revisions": revisions,
            "reference": reference_value,
            "result": result_value,
            "corrections": json.loads(row[15]),
            "correctionEvent": json.loads(row[16]) if row[16] else None,
        }
        if include_internal and row[14] is not None:
            value["observationSnapshot"] = json.loads(row[14])
        return value

    def update_disposition(
        self,
        record_id: str,
        disposition: str | None,
        reviewer_note: str,
        *,
        scope_id: str,
    ) -> bool:
        if disposition not in {None, "approved", "rejected", "more_info_requested"}:
            return False
        with self._lock, self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                """SELECT r.root_id, l.latest_record_id FROM history_revisions r
                JOIN history_lineages l ON l.root_id = r.root_id
                WHERE r.id = ? AND l.scope_id = ?""",
                (record_id, scope_id),
            ).fetchone()
            if row is None:
                return False
            connection.execute(
                "UPDATE history_revisions SET disposition = ?, reviewer_note = ? WHERE id = ?",
                (disposition, reviewer_note[:1000], record_id),
            )
            if str(row[1]) == record_id:
                connection.execute(
                    """UPDATE history_lineages SET disposition = ?, reviewer_note = ?
                    WHERE root_id = ?""",
                    (disposition, reviewer_note[:1000], row[0]),
                )
        return True

    def delete(self, record_id: str, *, scope_id: str) -> bool:
        orphan_paths: builtins.list[Path] = []
        with self._lock, self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                """SELECT r.root_id FROM history_revisions r
                JOIN history_lineages l ON l.root_id = r.root_id
                WHERE r.id = ? AND l.scope_id = ?""",
                (record_id, scope_id),
            ).fetchone()
            if row is None:
                return False
            orphan_paths = self._delete_lineage(connection, str(row[0]))
        self._unlink_after_commit(orphan_paths)
        return True

    def clear(self, *, scope_id: str) -> int:
        orphan_paths: builtins.list[Path] = []
        with self._lock, self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            roots = [
                str(row[0])
                for row in connection.execute(
                    "SELECT root_id FROM history_lineages WHERE scope_id = ?", (scope_id,)
                ).fetchall()
            ]
            for root_id in roots:
                orphan_paths.extend(self._delete_lineage(connection, root_id))
        self._unlink_after_commit(orphan_paths)
        return len(roots)

    def panel_path(self, record_id: str, panel_id: str, *, scope_id: str) -> Path | None:
        with self._lock, self._connect() as connection:
            row = connection.execute(
                """
                SELECT b.relative_path FROM revision_panels p
                JOIN image_blobs b ON b.sha256 = p.blob_sha256
                JOIN history_revisions r ON r.id = p.record_id
                JOIN history_lineages l ON l.root_id = r.root_id
                WHERE p.record_id = ? AND p.panel_id = ? AND l.scope_id = ?
                """,
                (record_id, panel_id, scope_id),
            ).fetchone()
        if row is None:
            return None
        candidate = (self.root / str(row[0])).resolve()
        if self.blobs.resolve() not in candidate.parents or not candidate.is_file():
            return None
        return candidate

    def _insert_revision(
        self,
        connection: sqlite3.Connection,
        *,
        record_id: str,
        root_id: str,
        revision: int,
        revision_kind: str,
        parent_id: str | None,
        created_at: str,
        reference: ReferenceRecord | AnalysisDraft,
        result: VerificationResult,
        observation: dict[str, object] | None,
        corrections: builtins.list[dict[str, object]],
        correction_event: dict[str, object] | None,
        panel_paths: tuple[Path, ...],
    ) -> None:
        connection.execute(
            """
            INSERT INTO history_revisions (
                id, root_id, revision, revision_kind, parent_id, created_at, request_id,
                reference_json, result_json, observation_json, corrections_json,
                correction_event_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record_id,
                root_id,
                revision,
                revision_kind,
                parent_id,
                created_at,
                result.request_id,
                json.dumps(reference.model_dump(by_alias=True, mode="json")),
                json.dumps(result.model_dump(by_alias=True, mode="json")),
                json.dumps(observation) if observation is not None else None,
                json.dumps(corrections),
                json.dumps(correction_event) if correction_event is not None else None,
            ),
        )
        for ordinal, source in enumerate(panel_paths, start=1):
            digest = self._store_blob(connection, source)
            connection.execute(
                """INSERT INTO revision_panels
                (record_id, panel_id, ordinal, blob_sha256, original_name)
                VALUES (?, ?, ?, ?, ?)""",
                (record_id, f"panel-{ordinal}", ordinal, digest, source.name),
            )

    def _store_blob(self, connection: sqlite3.Connection, source: Path) -> str:
        data = source.read_bytes()
        digest = sha256(data).hexdigest()
        media_type = image_media_type(data[:16]) or "application/octet-stream"
        suffix = {
            "image/jpeg": ".jpg",
            "image/png": ".png",
            "image/webp": ".webp",
        }.get(media_type, ".img")
        relative = Path("images") / "blobs" / f"{digest}{suffix}"
        target = self.root / relative
        row = connection.execute(
            "SELECT ref_count FROM image_blobs WHERE sha256 = ?", (digest,)
        ).fetchone()
        if row is None:
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.exists():
                shutil.copyfile(source, target)
            connection.execute(
                """INSERT INTO image_blobs
                (sha256, relative_path, media_type, byte_count, ref_count)
                VALUES (?, ?, ?, ?, 1)""",
                (digest, relative.as_posix(), media_type, len(data)),
            )
        else:
            connection.execute(
                "UPDATE image_blobs SET ref_count = ref_count + 1 WHERE sha256 = ?",
                (digest,),
            )
        return digest

    def _delete_lineage(
        self, connection: sqlite3.Connection, root_id: str
    ) -> builtins.list[Path]:
        orphan_paths: builtins.list[Path] = []
        blobs = connection.execute(
            """SELECT p.blob_sha256, COUNT(*) FROM revision_panels p
            JOIN history_revisions r ON r.id = p.record_id
            WHERE r.root_id = ? GROUP BY p.blob_sha256""",
            (root_id,),
        ).fetchall()
        connection.execute("DELETE FROM history_lineages WHERE root_id = ?", (root_id,))
        for digest, count in blobs:
            connection.execute(
                "UPDATE image_blobs SET ref_count = ref_count - ? WHERE sha256 = ?",
                (count, digest),
            )
            row = connection.execute(
                "SELECT relative_path, ref_count FROM image_blobs WHERE sha256 = ?", (digest,)
            ).fetchone()
            if row is not None and int(row[1]) == 0:
                path = (self.root / str(row[0])).resolve()
                if self.blobs.resolve() in path.parents:
                    orphan_paths.append(path)
                connection.execute("DELETE FROM image_blobs WHERE sha256 = ?", (digest,))
        return orphan_paths

    def _evict(self, connection: sqlite3.Connection) -> builtins.list[Path]:
        orphan_paths: builtins.list[Path] = []
        roots = connection.execute(
            """SELECT root_id FROM history_lineages
            ORDER BY root_created_at DESC, root_id DESC LIMIT -1 OFFSET ?""",
            (HISTORY_LIMIT,),
        ).fetchall()
        for row in roots:
            orphan_paths.extend(self._delete_lineage(connection, str(row[0])))
        return orphan_paths

    def _unlink_after_commit(self, paths: builtins.list[Path]) -> None:
        for path in paths:
            try:
                path.unlink(missing_ok=True)
            except OSError:
                # Startup reconciliation retries deletion without making a committed
                # metadata operation look unsuccessful to the caller.
                continue

    def _cleanup_orphan_files(self) -> None:
        """Remove blobs left by a crash after commit or before metadata insertion."""

        with self._lock, self._connect() as connection:
            retained = {
                (self.root / str(row[0])).resolve()
                for row in connection.execute("SELECT relative_path FROM image_blobs").fetchall()
            }
        blob_root = self.blobs.resolve()
        for path in self.blobs.iterdir():
            resolved = path.resolve()
            if path.is_file() and resolved not in retained and blob_root in resolved.parents:
                try:
                    resolved.unlink(missing_ok=True)
                except OSError:
                    continue

    def _panels(
        self, connection: sqlite3.Connection, record_id: str
    ) -> builtins.list[dict[str, object]]:
        rows = connection.execute(
            """SELECT p.panel_id, p.original_name, b.media_type, b.byte_count,
                      p.blob_sha256
            FROM revision_panels p JOIN image_blobs b ON b.sha256 = p.blob_sha256
            WHERE p.record_id = ? ORDER BY p.ordinal""",
            (record_id,),
        ).fetchall()
        return [
            {
                "panelId": row[0],
                "fileName": row[1],
                "mediaType": row[2],
                "byteCount": row[3],
                "imageSha256": row[4],
                "imageUrl": f"/api/v1/history/{record_id}/panels/{row[0]}",
                "label": f"Image {index}",
            }
            for index, row in enumerate(rows, start=1)
        ]

    def _summary(self, connection: sqlite3.Connection, row: sqlite3.Row) -> dict[str, object]:
        panels = self._panels(connection, str(row[8]))
        return {
            "id": row[8],
            "rootId": row[0],
            "createdAt": row[1],
            "requestId": row[2],
            "displayName": row[3],
            "beverageType": row[4],
            "summary": row[5],
            "disposition": row[6],
            "reviewerNote": row[7],
            "panelCount": len(panels),
            "panels": panels,
            "revision": row[9],
            "revisionKind": row[10],
        }

    @staticmethod
    def _display_values(reference: ReferenceRecord | AnalysisDraft) -> tuple[str, str]:
        case_label = reference.case_label if isinstance(reference, ReferenceRecord) else None
        display_name = case_label or reference.brand_name or "Product label"
        return display_name, reference.beverage_type or "unresolved"

    def _migrate_legacy(self, connection: sqlite3.Connection) -> None:
        table = connection.execute(
            "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'history'"
        ).fetchone()
        if table is None:
            return
        rows = connection.execute("SELECT * FROM history ORDER BY created_at, id").fetchall()
        for row in rows:
            record_id = str(row["id"])
            if connection.execute(
                "SELECT 1 FROM history_lineages WHERE root_id = ?", (record_id,)
            ).fetchone():
                continue
            reference = json.loads(row["reference_json"])
            result = json.loads(row["result_json"])
            connection.execute(
                """INSERT INTO history_lineages (
                root_id, scope_id, root_created_at, latest_record_id, latest_revision,
                display_name, beverage_type, summary, disposition, reviewer_note
                ) VALUES (?, ?, ?, ?, 1, ?, ?, ?, ?, ?)""",
                (
                    record_id,
                    row["scope_id"],
                    row["created_at"],
                    record_id,
                    row["display_name"],
                    row["beverage_type"],
                    row["summary"],
                    row["disposition"],
                    row["reviewer_note"],
                ),
            )
            result.update(
                {
                    "historyId": record_id,
                    "rootId": record_id,
                    "revision": 1,
                    "revisionKind": "original",
                }
            )
            connection.execute(
                """INSERT INTO history_revisions (
                id, root_id, revision, revision_kind, created_at, request_id,
                reference_json, result_json, disposition, reviewer_note
                ) VALUES (?, ?, 1, 'original', ?, ?, ?, ?, ?, ?)""",
                (
                    record_id,
                    record_id,
                    row["created_at"],
                    row["request_id"],
                    json.dumps(reference),
                    json.dumps(result),
                    row["disposition"],
                    row["reviewer_note"],
                ),
            )
            for index, panel in enumerate(json.loads(row["panels_json"]), start=1):
                source = self.images / record_id / str(panel["fileName"])
                if not source.is_file():
                    continue
                digest = self._store_blob(connection, source)
                connection.execute(
                    """INSERT INTO revision_panels
                    (record_id, panel_id, ordinal, blob_sha256, original_name)
                    VALUES (?, ?, ?, ?, ?)""",
                    (record_id, f"panel-{index}", index, digest, source.name),
                )

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database, timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection
