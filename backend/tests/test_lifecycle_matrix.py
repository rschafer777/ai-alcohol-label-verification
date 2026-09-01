from __future__ import annotations

import asyncio
import json
import multiprocessing as mp
import queue
import threading
import time
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Any

import psutil
import pytest
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from labelverify.api.errors import PublicApiError
from labelverify.api.routes import router
from labelverify.contracts.models import ReferenceRecord
from labelverify.orchestration import supervisor as supervisor_module
from labelverify.orchestration.supervisor import (
    SupervisorSnapshot,
    WorkerNotReady,
    WorkerSupervisor,
    WorkerTimedOut,
)
from labelverify.security.boundary import BoundaryMiddleware
from labelverify.security.rate_limit import AdmissionController, StartRateLimiter
from labelverify.settings.config import Settings

from .helpers import fake_result, jpeg_bytes, reference

BOUNDARY = b"labelverify-lifecycle"
RESERVATION_BYTES = 17_301_504


def _runtime(tmp_path: Path) -> Settings:
    static_root = tmp_path / "dist"
    static_root.mkdir(exist_ok=True)
    return Settings(
        runtime_mode="direct",
        allowed_host=None,
        model_root=tmp_path / "models",
        spool_root=tmp_path / "spool",
        sample_manifest=tmp_path / "sample.json",
        static_root=static_root,
        build_id="lifecycle-matrix",
    )


def _multipart_body(
    panels: list[bytes],
    *,
    reference_value: ReferenceRecord | None = None,
    filename: str = "label.jpg",
) -> bytes:
    value = reference_value or reference()
    chunks = [
        b"--" + BOUNDARY + b"\r\n",
        b'Content-Disposition: form-data; name="reference"\r\n\r\n',
        value.model_dump_json(by_alias=True).encode("utf-8"),
        b"\r\n",
    ]
    for panel in panels:
        chunks.extend(
            [
                b"--" + BOUNDARY + b"\r\n",
                (
                    f'Content-Disposition: form-data; name="panels"; filename="{filename}"\r\n'
                ).encode(),
                b"Content-Type: image/jpeg\r\n\r\n",
                panel,
                b"\r\n",
            ]
        )
    chunks.extend([b"--" + BOUNDARY + b"--\r\n"])
    return b"".join(chunks)


class _OneShotReceive:
    def __init__(self, body: bytes) -> None:
        self.body = body
        self.calls = 0

    async def __call__(self) -> dict[str, Any]:
        self.calls += 1
        if self.calls == 1:
            return {"type": "http.request", "body": self.body, "more_body": False}
        return {"type": "http.request", "body": b"", "more_body": False}


class _GatedReceive:
    def __init__(self, body: bytes, gate: asyncio.Event) -> None:
        marker = b"\r\n--" + BOUNDARY + b"--\r\n"
        assert body.endswith(marker)
        self.initial = body[: -len(marker)]
        self.closing = marker
        self.gate = gate
        self.calls = 0

    async def __call__(self) -> dict[str, Any]:
        self.calls += 1
        if self.calls == 1:
            return {"type": "http.request", "body": self.initial, "more_body": True}
        await self.gate.wait()
        return {"type": "http.request", "body": self.closing, "more_body": False}


class _ImmediateSupervisor:
    ready = True

    def start(self) -> bool:
        return True

    def stop(self) -> None:
        return None

    def snapshot(self) -> SupervisorSnapshot:
        return SupervisorSnapshot(True, 1, 0, 0, 0, 4100)

    def run(
        self, request_id: str, reference_value: ReferenceRecord, paths: tuple[Path, ...]
    ) -> object:
        assert reference_value.brand_name
        assert paths and all(path.is_file() for path in paths)
        return fake_result(request_id)


class _BlockingSupervisor:
    ready = True

    def __init__(self, expected_jobs: int) -> None:
        self.expected_jobs = expected_jobs
        self.entered = threading.Event()
        self.release = threading.Event()
        self._active_jobs = 0
        self._lock = threading.Lock()

    def start(self) -> bool:
        return True

    def stop(self) -> None:
        self.release.set()

    def snapshot(self) -> SupervisorSnapshot:
        with self._lock:
            active_jobs = self._active_jobs
        return SupervisorSnapshot(True, 1, active_jobs, 0, 0, 4200)

    def run(
        self, request_id: str, reference_value: ReferenceRecord, paths: tuple[Path, ...]
    ) -> object:
        assert reference_value.brand_name
        assert paths and all(path.is_file() for path in paths)
        with self._lock:
            self._active_jobs += 1
            if self._active_jobs >= self.expected_jobs:
                self.entered.set()
        try:
            if not self.release.wait(timeout=5.0):
                raise RuntimeError("Lifecycle test worker was not released")
            assert all(path.is_file() for path in paths)
            return fake_result(request_id)
        finally:
            with self._lock:
                self._active_jobs -= 1


def _boundary_app(
    tmp_path: Path,
    supervisor: object,
    limiter: StartRateLimiter,
    admissions: AdmissionController,
) -> tuple[BoundaryMiddleware, Settings]:
    settings = _runtime(tmp_path)
    app = FastAPI()
    app.state.settings = settings
    app.state.supervisor = supervisor
    app.include_router(router)

    @app.exception_handler(PublicApiError)
    async def public_error_handler(_: Request, exc: PublicApiError) -> JSONResponse:
        return JSONResponse(
            exc.public().model_dump(by_alias=True, exclude_none=True), status_code=exc.http_status
        )

    return BoundaryMiddleware(app, settings, limiter=limiter, admissions=admissions), settings


def _scope(body: bytes, client: str) -> dict[str, Any]:
    return {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "POST",
        "scheme": "http",
        "path": "/api/v1/verifications",
        "raw_path": b"/api/v1/verifications",
        "query_string": b"",
        "root_path": "",
        "headers": [
            (b"content-type", b"multipart/form-data; boundary=" + BOUNDARY),
            (b"content-length", str(len(body)).encode("ascii")),
        ],
        "client": (client, 50000),
        "server": ("testserver", 80),
        "state": {},
    }


async def _invoke(
    app: BoundaryMiddleware,
    body: bytes,
    client: str,
    receive: Callable[[], Awaitable[dict[str, Any]]] | None = None,
    send_override: Callable[[dict[str, Any]], Awaitable[None]] | None = None,
) -> list[dict[str, Any]]:
    sent: list[dict[str, Any]] = []

    async def send(message: dict[str, Any]) -> None:
        sent.append(message)

    await app(_scope(body, client), receive or _OneShotReceive(body), send_override or send)
    return sent


def _response_status(messages: list[dict[str, Any]]) -> int:
    return int(
        next(message["status"] for message in messages if message["type"] == "http.response.start")
    )


def _response_json(messages: list[dict[str, Any]]) -> dict[str, Any]:
    body = b"".join(
        message.get("body", b"") for message in messages if message["type"] == "http.response.body"
    )
    return dict(json.loads(body))


def _spool_entries(spool_root: Path) -> list[Path]:
    return list(spool_root.rglob("*")) if spool_root.exists() else []


def _spool_open_files(spool_root: Path) -> list[str]:
    resolved = spool_root.resolve()
    paths: list[str] = []
    process = psutil.Process()
    for opened in process.open_files():
        path = Path(opened.path).resolve()
        if path == resolved or resolved in path.parents:
            paths.append(str(path))
    return paths


async def _wait_for_thread_event(event: threading.Event) -> None:
    assert await asyncio.to_thread(event.wait, 2.0)


async def _async_wait_until(predicate: Callable[[], bool], timeout: float = 5.0) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return True
        await asyncio.sleep(0.01)
    return predicate()


def _wait_until(predicate: Callable[[], bool], timeout: float = 5.0) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return True
        time.sleep(0.01)
    return predicate()


@pytest.mark.asyncio
async def test_t029_upload_timeout_closes_partial_spool_and_ownership(tmp_path: Path) -> None:
    limiter = StartRateLimiter()
    admissions = AdmissionController()
    app, settings = _boundary_app(tmp_path, _ImmediateSupervisor(), limiter, admissions)
    app.upload_deadline = 0.05
    body = _multipart_body([b"\xff\xd8\xff\xe0" + b"x" * 1_100_000])
    gate = asyncio.Event()

    messages = await _invoke(app, body, "127.0.0.10", _GatedReceive(body, gate))

    assert _response_status(messages) == 408
    assert _response_json(messages)["code"] == "upload_timeout"
    assert admissions.counters == (0, 0)
    assert limiter.counters.active == 0
    assert _spool_entries(settings.spool_root) == []
    assert _spool_open_files(settings.spool_root) == []


@pytest.mark.asyncio
async def test_t041_two_slow_uploads_hold_capacity_and_third_reads_no_body(
    tmp_path: Path,
) -> None:
    limiter = StartRateLimiter()
    admissions = AdmissionController()
    app, settings = _boundary_app(tmp_path, _ImmediateSupervisor(), limiter, admissions)
    body = _multipart_body([jpeg_bytes()])
    gates = [asyncio.Event(), asyncio.Event()]
    receives = [_GatedReceive(body, gate) for gate in gates]
    first = asyncio.create_task(_invoke(app, body, "127.0.0.11", receives[0]))
    second = asyncio.create_task(_invoke(app, body, "127.0.0.12", receives[1]))
    assert await _async_wait_until(lambda: admissions.counters == (2, 2 * RESERVATION_BYTES))

    rejected_receive = _OneShotReceive(body)
    rejected = await _invoke(app, body, "127.0.0.13", rejected_receive)
    assert _response_status(rejected) == 503
    assert _response_json(rejected)["code"] == "verification_capacity_busy"
    assert rejected_receive.calls == 0
    assert admissions.counters == (2, 2 * RESERVATION_BYTES)

    for gate in gates:
        gate.set()
    completed = await asyncio.gather(first, second)
    assert [_response_status(messages) for messages in completed] == [200, 200]
    assert admissions.counters == (0, 0)
    assert limiter.counters.active == 0
    assert _spool_entries(settings.spool_root) == []


@pytest.mark.asyncio
async def test_t029_near_limit_requests_cleanup_files_handles_and_reservations(
    tmp_path: Path,
) -> None:
    limiter = StartRateLimiter()
    admissions = AdmissionController()
    supervisor = _BlockingSupervisor(expected_jobs=2)
    app, settings = _boundary_app(tmp_path, supervisor, limiter, admissions)
    panel = b"\xff\xd8\xff\xe0" + b"n" * (4_194_304 - 4)
    body = _multipart_body([panel, panel])
    assert len(body) <= 8_650_752

    first = asyncio.create_task(_invoke(app, body, "127.0.0.14"))
    second = asyncio.create_task(_invoke(app, body, "127.0.0.15"))
    await _wait_for_thread_event(supervisor.entered)
    assert admissions.counters == (2, 2 * RESERVATION_BYTES)
    assert limiter.counters.active == 2
    assert supervisor.snapshot().active_jobs == 2
    assert _spool_entries(settings.spool_root)

    supervisor.release.set()
    completed = await asyncio.gather(first, second)
    assert [_response_status(messages) for messages in completed] == [200, 200]
    assert admissions.counters == (0, 0)
    assert limiter.counters.active == 0
    assert supervisor.snapshot().active_jobs == 0
    assert _spool_entries(settings.spool_root) == []
    assert _spool_open_files(settings.spool_root) == []


@pytest.mark.asyncio
@pytest.mark.parametrize("client", ["127.0.0.16", "127.0.0.19", "127.0.0.20"])
async def test_t041_route_cancellation_retains_ownership_until_worker_finishes(
    tmp_path: Path, client: str
) -> None:
    limiter = StartRateLimiter()
    admissions = AdmissionController()
    supervisor = _BlockingSupervisor(expected_jobs=1)
    app, settings = _boundary_app(tmp_path, supervisor, limiter, admissions)
    body = _multipart_body([jpeg_bytes()])
    task = asyncio.create_task(_invoke(app, body, client))
    await _wait_for_thread_event(supervisor.entered)

    task.cancel()
    await asyncio.sleep(0.05)
    assert not task.done()
    assert admissions.counters == (1, RESERVATION_BYTES)
    assert limiter.counters.active == 1
    assert supervisor.snapshot().active_jobs == 1
    assert _spool_entries(settings.spool_root)

    supervisor.release.set()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert admissions.counters == (0, 0)
    assert limiter.counters.active == 0
    assert supervisor.snapshot().active_jobs == 0
    assert _spool_entries(settings.spool_root) == []
    assert _spool_open_files(settings.spool_root) == []


@pytest.mark.asyncio
@pytest.mark.parametrize("client", ["127.0.0.17", "127.0.0.21", "127.0.0.22"])
async def test_t041_disconnect_delivery_failure_keeps_ownership_until_worker_finishes(
    tmp_path: Path, client: str
) -> None:
    limiter = StartRateLimiter()
    admissions = AdmissionController()
    supervisor = _BlockingSupervisor(expected_jobs=1)
    app, settings = _boundary_app(tmp_path, supervisor, limiter, admissions)
    body = _multipart_body([jpeg_bytes()])

    async def disconnected_send(message: dict[str, Any]) -> None:
        del message
        raise ConnectionError("client disconnected")

    task = asyncio.create_task(_invoke(app, body, client, send_override=disconnected_send))
    await _wait_for_thread_event(supervisor.entered)
    assert admissions.counters == (1, RESERVATION_BYTES)
    assert limiter.counters.active == 1
    assert supervisor.snapshot().active_jobs == 1
    assert _spool_entries(settings.spool_root)

    supervisor.release.set()
    with pytest.raises(ConnectionError, match="client disconnected"):
        await task
    assert admissions.counters == (0, 0)
    assert limiter.counters.active == 0
    assert supervisor.snapshot().active_jobs == 0
    assert _spool_entries(settings.spool_root) == []
    assert _spool_open_files(settings.spool_root) == []


def _stall_then_recover_worker(
    commands: Any, results: Any, model_root: str, generation: int
) -> None:
    del model_root
    results.put({"kind": "ready", "generation": generation})
    while True:
        command = commands.get()
        if command.get("kind") == "stop":
            return
        if generation == 1:
            time.sleep(60.0)
            continue
        request_id = str(command["requestId"])
        results.put(
            {
                "kind": "result",
                "jobId": command["jobId"],
                "payload": fake_result(request_id).model_dump(by_alias=True, mode="json"),
            }
        )


def _stall_forever_worker(commands: Any, results: Any, model_root: str, generation: int) -> None:
    del model_root
    results.put({"kind": "ready", "generation": generation})
    command = commands.get()
    if command.get("kind") == "stop":
        return
    time.sleep(60.0)


def test_t009_real_worker_timeout_replaces_recovers_and_stops(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(supervisor_module, "_worker_main", _stall_then_recover_worker)
    supervisor = WorkerSupervisor(tmp_path / "models", worker_deadline_seconds=0.2)
    assert supervisor.start(readiness_timeout=5.0)
    first_pid = supervisor.snapshot().child_pid
    with pytest.raises(WorkerTimedOut):
        supervisor.run("stalled", reference(), (tmp_path / "panel.jpg",))
    assert _wait_until(lambda: supervisor.ready and supervisor.snapshot().generation == 2)
    recovered = supervisor.run("recovered", reference(), (tmp_path / "panel.jpg",))
    recovered_pid = supervisor.snapshot().child_pid
    assert recovered.request_id == "recovered"
    assert first_pid is not None and recovered_pid is not None and first_pid != recovered_pid
    assert supervisor.snapshot().timeouts == 1
    assert supervisor.snapshot().restarts == 1
    assert supervisor.snapshot().active_jobs == 0

    supervisor.stop()
    assert supervisor.snapshot().child_pid is None
    assert supervisor.snapshot().active_jobs == 0
    assert not supervisor._replacement_threads
    assert first_pid not in {child.pid for child in mp.active_children()}
    assert recovered_pid not in {child.pid for child in mp.active_children()}


def test_t029_shutdown_overlap_interrupts_owned_job_and_reaches_zero(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(supervisor_module, "_worker_main", _stall_forever_worker)
    supervisor = WorkerSupervisor(tmp_path / "models", worker_deadline_seconds=2.0)
    assert supervisor.start(readiness_timeout=5.0)
    child_pid = supervisor.snapshot().child_pid
    errors: list[BaseException] = []

    def run_job() -> None:
        try:
            supervisor.run("shutdown", reference(), (tmp_path / "panel.jpg",))
        except BaseException as exc:
            errors.append(exc)

    runner = threading.Thread(target=run_job)
    runner.start()
    assert _wait_until(lambda: supervisor.snapshot().active_jobs == 1)
    started = time.monotonic()
    supervisor.stop(join_timeout=0.5)
    elapsed = time.monotonic() - started
    runner.join(timeout=1.0)

    assert elapsed < 1.0
    assert not runner.is_alive()
    assert len(errors) == 1 and isinstance(errors[0], WorkerNotReady)
    assert supervisor.snapshot().active_jobs == 0
    assert supervisor.snapshot().child_pid is None
    assert not supervisor._replacement_threads
    assert child_pid not in {child.pid for child in mp.active_children()}


class _AlwaysFullCommandQueue:
    def __init__(self) -> None:
        self.entered = threading.Event()

    def put(self, command: dict[str, Any], timeout: float) -> None:
        del command
        self.entered.set()
        time.sleep(min(timeout, 0.01))
        raise queue.Full

    def put_nowait(self, command: dict[str, Any]) -> None:
        del command
        raise queue.Full


class _AliveProcess:
    pid = 4300

    def __init__(self) -> None:
        self.alive = True

    def is_alive(self) -> bool:
        return self.alive

    def join(self, timeout: float) -> None:
        del timeout

    def terminate(self) -> None:
        self.alive = False

    def kill(self) -> None:
        self.alive = False


def test_t029_shutdown_interrupts_command_enqueue_race(tmp_path: Path) -> None:
    commands = _AlwaysFullCommandQueue()
    process = _AliveProcess()
    supervisor = WorkerSupervisor(tmp_path / "models", worker_deadline_seconds=2.0)
    supervisor._commands = commands
    supervisor._results = object()
    supervisor._process = process
    supervisor._ready = True
    errors: list[BaseException] = []

    def run_job() -> None:
        try:
            supervisor.run("enqueue-race", reference(), (tmp_path / "panel.jpg",))
        except BaseException as exc:
            errors.append(exc)

    runner = threading.Thread(target=run_job)
    runner.start()
    assert commands.entered.wait(timeout=1.0)
    supervisor.stop(join_timeout=0.5)
    runner.join(timeout=1.0)

    assert not runner.is_alive()
    assert len(errors) == 1 and isinstance(errors[0], WorkerNotReady)
    assert supervisor.snapshot().active_jobs == 0
    assert supervisor.snapshot().child_pid is None
    assert not supervisor._replacement_threads


def test_t041_full_command_queue_reaches_worker_timeout(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    commands = _AlwaysFullCommandQueue()
    process = _AliveProcess()
    supervisor = WorkerSupervisor(tmp_path / "models", worker_deadline_seconds=0.05)
    supervisor._commands = commands
    supervisor._results = object()
    supervisor._process = process
    supervisor._ready = True
    monkeypatch.setattr(supervisor, "_schedule_replacement", lambda: None)

    with pytest.raises(WorkerTimedOut):
        supervisor.run("queue-stall", reference(), (tmp_path / "panel.jpg",))

    assert supervisor.snapshot().timeouts == 1
    assert supervisor.snapshot().active_jobs == 0
    assert supervisor.snapshot().child_pid is None
    assert not process.is_alive()


@pytest.mark.asyncio
async def test_t041_parent_phase_stall_reaches_server_deadline(tmp_path: Path) -> None:
    limiter = StartRateLimiter()
    admissions = AdmissionController()
    settings = _runtime(tmp_path)

    async def stalled_parent(scope: dict[str, Any], receive: Any, send: Any) -> None:
        del scope, receive, send
        await asyncio.sleep(60.0)

    app = BoundaryMiddleware(
        stalled_parent,
        settings,
        limiter=limiter,
        admissions=admissions,
    )
    app.server_deadline = 0.05
    body = _multipart_body([jpeg_bytes()])
    started = time.monotonic()

    messages = await _invoke(app, body, "127.0.0.23")

    assert time.monotonic() - started < 1.0
    assert _response_status(messages) == 504
    assert _response_json(messages)["code"] == "request_deadline_exceeded"
    assert admissions.counters == (0, 0)
    assert limiter.counters.active == 0


@pytest.mark.asyncio
async def test_t041_response_transfer_stall_terminates_and_cleans(tmp_path: Path) -> None:
    limiter = StartRateLimiter()
    admissions = AdmissionController()
    app, settings = _boundary_app(tmp_path, _ImmediateSupervisor(), limiter, admissions)
    app.server_deadline = 0.05
    body = _multipart_body([jpeg_bytes()])
    response_started = asyncio.Event()

    async def stalled_send(message: dict[str, Any]) -> None:
        if message["type"] == "http.response.start":
            response_started.set()
        await asyncio.sleep(60.0)

    started = time.monotonic()
    messages = await _invoke(app, body, "127.0.0.24", send_override=stalled_send)

    assert response_started.is_set()
    assert time.monotonic() - started < 1.0
    assert messages == []
    assert admissions.counters == (0, 0)
    assert limiter.counters.active == 0
    assert _spool_entries(settings.spool_root) == []
    assert _spool_open_files(settings.spool_root) == []


@pytest.mark.asyncio
async def test_t029_content_and_path_canaries_never_reach_response_or_logs(
    tmp_path: Path, caplog: pytest.LogCaptureFixture, capsys: pytest.CaptureFixture[str]
) -> None:
    limiter = StartRateLimiter()
    admissions = AdmissionController()
    app, settings = _boundary_app(tmp_path, _ImmediateSupervisor(), limiter, admissions)
    canary = "PRIVATE-CONTENT-CANARY-7c9d"
    filename = "C:\\Users\\private\\label-canary.jpg"
    body = _multipart_body(
        [b"not-an-image"], reference_value=reference(brand=canary), filename=filename
    )

    messages = await _invoke(app, body, "127.0.0.18")
    response_text = json.dumps(_response_json(messages))
    captured = capsys.readouterr()
    assert _response_status(messages) == 415
    assert canary not in response_text
    assert filename not in response_text
    assert canary not in caplog.text
    assert filename not in caplog.text
    assert canary not in captured.out + captured.err
    assert filename not in captured.out + captured.err
    assert admissions.counters == (0, 0)
    assert limiter.counters.active == 0
    assert _spool_entries(settings.spool_root) == []
