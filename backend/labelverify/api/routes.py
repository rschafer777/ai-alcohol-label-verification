from __future__ import annotations

import asyncio
import json
import shutil
import tempfile
import time
from contextlib import suppress
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import FileResponse, JSONResponse
from pydantic import ValidationError
from starlette.datastructures import UploadFile
from starlette.formparsers import MultiPartException

from labelverify.api.errors import PublicApiError
from labelverify.api.multipart import ControlledMultiPartParser
from labelverify.contracts.loader import CONTRACT_HASHES, contracts
from labelverify.contracts.models import ReferenceRecord, VerificationResult
from labelverify.orchestration.supervisor import (
    WorkerExecutionFailed,
    WorkerNotReady,
    WorkerQueueBusy,
    WorkerSupervisor,
    WorkerTimedOut,
)
from labelverify.security.signatures import image_media_type
from labelverify.settings.config import Settings

router = APIRouter()


@router.get("/health/live")
async def live() -> dict[str, bool]:
    return {"live": True}


@router.get("/health/ready")
async def ready(request: Request) -> JSONResponse:
    supervisor: WorkerSupervisor = request.app.state.supervisor
    snapshot = supervisor.snapshot()
    payload = {
        "ready": snapshot.ready,
        "profileId": "distilled_spirits_demo_v1",
        "generation": snapshot.generation,
    }
    return JSONResponse(payload, status_code=200 if snapshot.ready else 503)


@router.get("/api/v1/meta")
async def meta(request: Request) -> dict[str, Any]:
    settings: Settings = request.app.state.settings
    supervisor: WorkerSupervisor = request.app.state.supervisor
    bundle = contracts()
    return {
        "buildId": settings.build_id,
        "apiContractVersion": bundle.api["contractVersion"],
        "profileId": "distilled_spirits_demo_v1",
        "profileVersion": bundle.checks["registryVersion"],
        "modelIdentity": "rapidocr-3.4.2",
        "ruleRegistryVersion": bundle.rules["registryVersion"],
        "selectedCheckCount": len(bundle.check_ids),
        "limits": bundle.api["limits"],
        "ready": supervisor.ready,
        "contractHashes": CONTRACT_HASHES,
    }


@router.get("/api/v1/samples/distilled-spirits-v1")
async def sample(request: Request) -> JSONResponse:
    settings: Settings = request.app.state.settings
    value = _load_sample_manifest(settings, request.state.request_id)
    public_panels = []
    try:
        for index, panel in enumerate(_sample_panels(value), start=1):
            panel_id = str(panel["panelId"])
            public_panels.append(
                {
                    key: item
                    for key, item in panel.items()
                    if key not in {"path", "label", "fileName", "url"}
                }
                | {
                    "label": _sample_panel_label(index),
                    "fileName": _sample_panel_path(settings, panel).name,
                    "url": f"/api/v1/samples/distilled-spirits-v1/panels/{panel_id}",
                }
            )
    except ValueError as exc:
        raise PublicApiError("not_ready", request.state.request_id) from exc
    return JSONResponse(value | {"panels": public_panels})


@router.get("/api/v1/samples/distilled-spirits-v1/panels/{panel_id}")
async def sample_panel(request: Request, panel_id: str) -> FileResponse:
    settings: Settings = request.app.state.settings
    value = _load_sample_manifest(settings, request.state.request_id)
    try:
        panels = {str(panel["panelId"]): panel for panel in _sample_panels(value)}
    except ValueError as exc:
        raise PublicApiError("not_ready", request.state.request_id) from exc
    if panel_id not in panels:
        raise PublicApiError("not_ready", request.state.request_id)
    panel = panels[panel_id]
    try:
        path = _sample_panel_path(settings, panel)
    except ValueError as exc:
        raise PublicApiError("not_ready", request.state.request_id) from exc
    if not path.is_file():
        raise PublicApiError("not_ready", request.state.request_id)
    return FileResponse(
        path,
        media_type=str(panel["mimeType"]),
        filename=path.name,
        content_disposition_type="inline",
    )


def _load_sample_manifest(settings: Settings, request_id: str) -> dict[str, Any]:
    try:
        value = json.loads(settings.sample_manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PublicApiError("not_ready", request_id) from exc
    if not isinstance(value, dict):
        raise PublicApiError("not_ready", request_id)
    return value


def _sample_panels(value: dict[str, Any]) -> list[dict[str, Any]]:
    panels = value.get("panels")
    if not isinstance(panels, list) or not 1 <= len(panels) <= 6:
        raise ValueError("The governed sample panel list is invalid")
    typed = [panel for panel in panels if isinstance(panel, dict)]
    if len(typed) != len(panels):
        raise ValueError("The governed sample panel entry is invalid")
    panel_ids = [panel.get("panelId") for panel in typed]
    expected = [f"panel-{index}" for index in range(1, len(typed) + 1)]
    if panel_ids != expected:
        raise ValueError("The governed sample panel IDs are invalid")
    return typed


def _sample_panel_path(settings: Settings, panel: dict[str, Any]) -> Path:
    declared = panel.get("path")
    if not isinstance(declared, str) or not declared:
        raise ValueError("The governed sample panel path is invalid")
    project_root = settings.sample_manifest.resolve().parents[2]
    path = (project_root / declared).resolve()
    allowed_root = (settings.sample_manifest.parent / "panels").resolve()
    if path.parent != allowed_root:
        raise ValueError("The governed sample panel path is outside the panel directory")
    return path


def _sample_panel_label(index: int) -> str:
    if index == 1:
        return "Front label"
    if index == 2:
        return "Back label"
    return f"Label panel {index}"


@router.post("/api/v1/verifications")
async def verify(request: Request) -> JSONResponse:
    request_id = request.state.request_id
    settings: Settings = request.app.state.settings
    supervisor: WorkerSupervisor = request.app.state.supervisor
    if not supervisor.ready:
        raise PublicApiError("not_ready", request_id)
    settings.spool_root.mkdir(parents=True, exist_ok=True, mode=0o700)
    reference, uploads = await _parse_form(request, request_id, settings.spool_root)
    request_dir: Path | None = None
    try:
        request_dir = Path(tempfile.mkdtemp(prefix="request-", dir=settings.spool_root))
        panel_paths = await _copy_panels(uploads, request_dir, request_id)
        result = await _run_owned(supervisor, request_id, reference, panel_paths)
        started = float(request.scope["state"].get("admission_started", time.monotonic()))
        total_ms = round((time.monotonic() - started) * 1000, 3)
        if total_ms > float(contracts().api["limits"]["serverDeadlineSeconds"]) * 1000:
            raise PublicApiError("request_deadline_exceeded", request_id)
        result = result.model_copy(update={"server_duration_ms": total_ms})
        return JSONResponse(result.model_dump(by_alias=True, mode="json"))
    finally:
        for upload in uploads:
            await upload.close()
        if request_dir is not None:
            shutil.rmtree(request_dir, ignore_errors=True)


async def _parse_form(
    request: Request, request_id: str, spool_root: Path
) -> tuple[ReferenceRecord, list[UploadFile]]:
    limits = contracts().api["limits"]
    form: Any | None = None
    try:
        parser = ControlledMultiPartParser(
            request.headers,
            request.stream(),
            spool_root=spool_root,
            max_files=int(limits["panelCountMax"]),
            max_fields=1,
            max_part_size=int(limits["fileBytes"]),
        )
        form = await parser.parse()
        parts = list(form.multi_items())
        reference_parts = [value for key, value in parts if key == "reference"]
        panel_parts = [value for key, value in parts if key == "panels"]
        if any(key not in {"reference", "panels"} for key, _ in parts):
            raise PublicApiError("invalid_multipart", request_id)
        if len(reference_parts) != 1 or isinstance(reference_parts[0], UploadFile):
            raise PublicApiError("invalid_multipart", request_id)
        if not 1 <= len(panel_parts) <= int(limits["panelCountMax"]):
            raise PublicApiError("invalid_panel_count", request_id, "panels")
        if not all(isinstance(value, UploadFile) for value in panel_parts):
            raise PublicApiError("invalid_multipart", request_id)
        reference_raw = str(reference_parts[0]).encode("utf-8")
        if len(reference_raw) > int(limits["referenceBytes"]):
            raise PublicApiError("multipart_limit_exceeded", request_id)
        try:
            decoded = json.loads(reference_raw)
            reference = ReferenceRecord.model_validate(decoded)
        except (json.JSONDecodeError, ValidationError, TypeError) as exc:
            locator = _reference_locator(exc)
            raise PublicApiError("invalid_reference", request_id, locator) from exc
        uploads = [value for value in panel_parts if isinstance(value, UploadFile)]
        return reference, uploads
    except PublicApiError:
        if form is not None:
            await form.close()
        raise
    except MultiPartException as exc:
        if form is not None:
            await form.close()
        raise PublicApiError("multipart_limit_exceeded", request_id) from exc
    except Exception as exc:
        if form is not None:
            await form.close()
        raise PublicApiError("invalid_multipart", request_id) from exc


async def _copy_panels(
    uploads: list[UploadFile], request_dir: Path, request_id: str
) -> tuple[Path, ...]:
    limits = contracts().api["limits"]
    file_limit = int(limits["fileBytes"])
    aggregate_limit = int(limits["aggregateFileBytes"])
    aggregate = 0
    paths: list[Path] = []
    for index, upload in enumerate(uploads, start=1):
        path = request_dir / f"panel-{index}.img"
        size = 0
        prefix = b""
        with path.open("xb") as output:
            while True:
                chunk = await upload.read(64 * 1024)
                if not chunk:
                    break
                if len(prefix) < 16:
                    prefix = (prefix + chunk)[:16]
                size += len(chunk)
                aggregate += len(chunk)
                if size > file_limit or aggregate > aggregate_limit:
                    raise PublicApiError("request_too_large", request_id)
                output.write(chunk)
        if image_media_type(prefix) is None:
            raise PublicApiError("unsupported_media_type", request_id, f"panel-{index}")
        paths.append(path)
    return tuple(paths)


async def _run_owned(
    supervisor: WorkerSupervisor,
    request_id: str,
    reference: ReferenceRecord,
    paths: tuple[Path, ...],
) -> VerificationResult:
    task = asyncio.create_task(asyncio.to_thread(supervisor.run, request_id, reference, paths))
    try:
        return await asyncio.shield(task)
    except asyncio.CancelledError:
        with suppress(Exception):
            await asyncio.shield(task)
        raise
    except WorkerNotReady as exc:
        raise PublicApiError("not_ready", request_id) from exc
    except WorkerQueueBusy as exc:
        raise PublicApiError("worker_queue_busy", request_id) from exc
    except WorkerTimedOut as exc:
        raise PublicApiError("inference_timeout", request_id) from exc
    except WorkerExecutionFailed as exc:
        raise PublicApiError(exc.code, request_id, exc.field_or_panel) from exc


def _reference_locator(exc: Exception) -> str | None:
    if isinstance(exc, ValidationError) and exc.errors():
        location = exc.errors()[0].get("loc", ())
        if location:
            return str(location[0])
    return "reference"
