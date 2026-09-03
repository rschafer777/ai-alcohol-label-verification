from __future__ import annotations

import json
import shutil
import sqlite3
import threading
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from labelverify.contracts.models import AnalysisDraft, ReferenceRecord, VerificationResult
from labelverify.security.signatures import image_media_type

HISTORY_LIMIT = 500


class HistoryRepository:
    """SQLite metadata and local evidence images with a strict FIFO cap."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.database = root / "labelverify.sqlite3"
        self.images = root / "images"
        self._lock = threading.RLock()

    def initialize(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.images.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS history (
                    id TEXT PRIMARY KEY,
                    scope_id TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    request_id TEXT NOT NULL UNIQUE,
                    display_name TEXT NOT NULL,
                    beverage_type TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    reference_json TEXT NOT NULL,
                    result_json TEXT NOT NULL,
                    panels_json TEXT NOT NULL,
                    disposition TEXT,
                    reviewer_note TEXT NOT NULL DEFAULT ''
                );
                """
            )
            columns = {
                str(row[1]) for row in connection.execute("PRAGMA table_info(history)").fetchall()
            }
            if "scope_id" not in columns:
                connection.execute(
                    "ALTER TABLE history ADD COLUMN scope_id TEXT NOT NULL DEFAULT 'unscoped'"
                )
            connection.executescript(
                """
                CREATE INDEX IF NOT EXISTS history_scope_created_at
                ON history(scope_id, created_at DESC, id DESC);
                CREATE INDEX IF NOT EXISTS history_created_at
                ON history(created_at DESC, id DESC);
                """
            )

    def add(
        self,
        reference: ReferenceRecord | AnalysisDraft,
        result: VerificationResult,
        panel_paths: tuple[Path, ...],
        *,
        scope_id: str,
    ) -> str:
        record_id = f"hist_{uuid4().hex}"
        record_dir = self.images / record_id
        record_dir.mkdir(parents=True, exist_ok=False)
        panels: list[dict[str, str]] = []
        try:
            for index, source in enumerate(panel_paths, start=1):
                media_type = image_media_type(source.read_bytes()[:16])
                suffix = (
                    {
                        "image/jpeg": ".jpg",
                        "image/png": ".png",
                        "image/webp": ".webp",
                    }.get(media_type, ".img")
                    if media_type is not None
                    else ".img"
                )
                target = record_dir / f"panel-{index}{suffix}"
                shutil.copyfile(source, target)
                panels.append(
                    {
                        "panelId": f"panel-{index}",
                        "fileName": target.name,
                        "imageUrl": f"/api/v1/history/{record_id}/panels/panel-{index}",
                    }
                )
            created_at = datetime.now(UTC).isoformat()
            case_label = reference.case_label if isinstance(reference, ReferenceRecord) else None
            display_name = case_label or reference.brand_name or "Product label"
            beverage_type = reference.beverage_type or "unresolved"
            with self._lock, self._connect() as connection:
                connection.execute(
                    """
                    INSERT INTO history (
                        id, scope_id, created_at, request_id, display_name, beverage_type,
                        summary, reference_json, result_json, panels_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        record_id,
                        scope_id,
                        created_at,
                        result.request_id,
                        display_name,
                        beverage_type,
                        result.summary,
                        json.dumps(reference.model_dump(by_alias=True, mode="json")),
                        json.dumps(result.model_dump(by_alias=True, mode="json")),
                        json.dumps(panels),
                    ),
                )
                self._evict(connection)
            return record_id
        except Exception:
            shutil.rmtree(record_dir, ignore_errors=True)
            raise

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
        clauses: list[str] = ["scope_id = ?"]
        values: list[object] = [scope_id]
        if beverage_type:
            clauses.append("beverage_type = ?")
            values.append(beverage_type)
        if summary:
            clauses.append("summary = ?")
            values.append(summary)
        if disposition:
            clauses.append("disposition = ?")
            values.append(disposition)
        if query:
            clauses.append("(display_name LIKE ? OR request_id LIKE ? OR reviewer_note LIKE ?)")
            pattern = f"%{query}%"
            values.extend([pattern, pattern, pattern])
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        with self._lock, self._connect() as connection:
            total = int(
                connection.execute(f"SELECT COUNT(*) FROM history {where}", values).fetchone()[0]
            )
            rows = connection.execute(
                f"""
                SELECT id, created_at, request_id, display_name, beverage_type,
                       summary, disposition, reviewer_note, panels_json
                FROM history {where}
                ORDER BY created_at DESC, id DESC
                LIMIT ? OFFSET ?
                """,
                [*values, page_size, offset],
            ).fetchall()
        items = [self._summary(row) for row in rows]
        return {
            "items": items,
            "total": total,
            "cap": HISTORY_LIMIT,
            "offset": offset,
            "pageSize": page_size,
            "hasMore": offset + len(items) < total,
        }

    def get(self, record_id: str, *, scope_id: str) -> dict[str, object] | None:
        with self._lock, self._connect() as connection:
            row = connection.execute(
                """
                SELECT id, created_at, request_id, display_name, beverage_type,
                       summary, disposition, reviewer_note, panels_json,
                       reference_json, result_json
                FROM history WHERE id = ? AND scope_id = ?
                """,
                (record_id, scope_id),
            ).fetchone()
        if row is None:
            return None
        return {
            **self._summary(row),
            "reference": json.loads(row[9]),
            "result": json.loads(row[10]),
        }

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
            cursor = connection.execute(
                """
                UPDATE history SET disposition = ?, reviewer_note = ?
                WHERE id = ? AND scope_id = ?
                """,
                (disposition, reviewer_note[:1000], record_id, scope_id),
            )
            return cursor.rowcount == 1

    def delete(self, record_id: str, *, scope_id: str) -> bool:
        with self._lock, self._connect() as connection:
            cursor = connection.execute(
                "DELETE FROM history WHERE id = ? AND scope_id = ?", (record_id, scope_id)
            )
        if cursor.rowcount:
            shutil.rmtree(self.images / record_id, ignore_errors=True)
            return True
        return False

    def clear(self, *, scope_id: str) -> int:
        with self._lock, self._connect() as connection:
            rows = connection.execute(
                "SELECT id FROM history WHERE scope_id = ?", (scope_id,)
            ).fetchall()
            connection.execute("DELETE FROM history WHERE scope_id = ?", (scope_id,))
        for row in rows:
            shutil.rmtree(self.images / str(row[0]), ignore_errors=True)
        return len(rows)

    def panel_path(self, record_id: str, panel_id: str, *, scope_id: str) -> Path | None:
        detail = self.get(record_id, scope_id=scope_id)
        if detail is None:
            return None
        panels = detail.get("panels")
        if not isinstance(panels, list):
            return None
        match = next(
            (item for item in panels if isinstance(item, dict) and item.get("panelId") == panel_id),
            None,
        )
        if not isinstance(match, dict) or not isinstance(match.get("fileName"), str):
            return None
        candidate = (self.images / record_id / str(match["fileName"])).resolve()
        allowed = (self.images / record_id).resolve()
        if candidate.parent != allowed or not candidate.is_file():
            return None
        return candidate

    def _evict(self, connection: sqlite3.Connection) -> None:
        rows = connection.execute(
            "SELECT id FROM history ORDER BY created_at DESC, id DESC LIMIT -1 OFFSET ?",
            (HISTORY_LIMIT,),
        ).fetchall()
        for row in rows:
            connection.execute("DELETE FROM history WHERE id = ?", (row[0],))
            shutil.rmtree(self.images / str(row[0]), ignore_errors=True)

    @staticmethod
    def _summary(row: sqlite3.Row) -> dict[str, object]:
        panels = json.loads(row[8])
        return {
            "id": row[0],
            "createdAt": row[1],
            "requestId": row[2],
            "displayName": row[3],
            "beverageType": row[4],
            "summary": row[5],
            "disposition": row[6],
            "reviewerNote": row[7],
            "panelCount": len(panels),
            "panels": panels,
        }

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database, timeout=10)
        connection.row_factory = sqlite3.Row
        return connection
