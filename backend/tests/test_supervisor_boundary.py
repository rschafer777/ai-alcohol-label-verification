from __future__ import annotations

import json
import queue
import threading
import time
from pathlib import Path
from typing import Any

import pytest
from labelverify.contracts.loader import contracts
from labelverify.extraction.rapidocr_adapter import ModelIntegrityError, RapidOcrAdapter
from labelverify.orchestration.supervisor import WorkerNotReady, WorkerSupervisor
from labelverify.security.boundary import BoundaryMiddleware
from labelverify.security.rate_limit import StartRateLimiter
from labelverify.settings.config import Settings

from .helpers import reference


def runtime(tmp_path: Path) -> Settings:
    return Settings(
        runtime_mode="direct",
        allowed_host=None,
        model_root=tmp_path / "models",
        spool_root=tmp_path / "spool",
        sample_manifest=tmp_path / "sample.json",
        static_root=tmp_path / "dist",
        build_id="test",
    )


def test_adapter_fails_closed_for_missing_assets(tmp_path: Path) -> None:
    adapter = RapidOcrAdapter(tmp_path)
    with pytest.raises(ModelIntegrityError):
        adapter.verify_assets()


def test_supervisor_not_ready_never_accepts_job(tmp_path: Path) -> None:
    supervisor = WorkerSupervisor(tmp_path / "models")
    assert not supervisor.ready
    with pytest.raises(WorkerNotReady):
        supervisor.run("request", reference(), (tmp_path / "panel.jpg",))
    supervisor.stop()
    assert supervisor.snapshot().active_jobs == 0


async def invoke_boundary(
    tmp_path: Path,
    headers: list[tuple[bytes, bytes]],
    messages: list[dict[str, Any]],
    limiter: StartRateLimiter | None = None,
) -> tuple[list[dict[str, Any]], int]:
    reads = 0
    sent: list[dict[str, Any]] = []

    async def app(scope: dict[str, Any], receive: Any, send: Any) -> None:
        nonlocal reads
        while True:
            message = await receive()
            reads += 1
            if not message.get("more_body", False):
                break
        await send({"type": "http.response.start", "status": 204, "headers": []})
        await send({"type": "http.response.body", "body": b""})

    queue = list(messages)

    async def receive() -> dict[str, Any]:
        return queue.pop(0)

    async def send(message: dict[str, Any]) -> None:
        sent.append(message)

    middleware = BoundaryMiddleware(app, runtime(tmp_path), limiter=limiter)
    scope = {
        "type": "http",
        "method": "POST",
        "path": "/api/v1/verifications",
        "headers": headers,
        "client": ("127.0.0.1", 1000),
    }
    await middleware(scope, receive, send)
    return sent, reads


@pytest.mark.asyncio
async def test_oversize_content_length_rejects_before_body(tmp_path: Path) -> None:
    oversize = int(contracts().api["limits"]["rawRequestBytes"]) + 1
    sent, reads = await invoke_boundary(
        tmp_path,
        [(b"content-length", str(oversize).encode("ascii"))],
        [{"type": "http.request", "body": b"unused", "more_body": False}],
    )
    assert sent[0]["status"] == 413
    assert reads == 0
    assert json.loads(sent[1]["body"])["code"] == "request_too_large"


@pytest.mark.asyncio
async def test_duplicate_content_length_rejects_before_body(tmp_path: Path) -> None:
    sent, reads = await invoke_boundary(
        tmp_path,
        [(b"content-length", b"4"), (b"content-length", b"4")],
        [{"type": "http.request", "body": b"test", "more_body": False}],
    )
    assert sent[0]["status"] == 400
    assert reads == 0
    assert json.loads(sent[1]["body"])["code"] == "invalid_content_length"


@pytest.mark.asyncio
async def test_streaming_raw_count_and_content_length_match(tmp_path: Path) -> None:
    sent, reads = await invoke_boundary(
        tmp_path,
        [(b"content-length", b"4")],
        [
            {"type": "http.request", "body": b"te", "more_body": True},
            {"type": "http.request", "body": b"st", "more_body": False},
        ],
    )
    assert sent[0]["status"] == 204
    assert reads == 2


@pytest.mark.asyncio
async def test_understated_content_length_is_result_free_error(tmp_path: Path) -> None:
    sent, _ = await invoke_boundary(
        tmp_path,
        [(b"content-length", b"3")],
        [{"type": "http.request", "body": b"test", "more_body": False}],
    )
    assert sent[0]["status"] == 400
    assert json.loads(sent[1]["body"])["code"] == "content_length_mismatch"


class RecordingLimiter(StartRateLimiter):
    def __init__(self, rejection: str | None = None) -> None:
        super().__init__()
        self.rejection = rejection
        self.begin_calls = 0
        self.finish_calls = 0

    def begin(self, key: str, now: float | None = None) -> str | None:
        del key, now
        self.begin_calls += 1
        return self.rejection

    def finish(self, key: str) -> None:
        del key
        self.finish_calls += 1


@pytest.mark.asyncio
async def test_invalid_length_does_not_charge_shared_start_budget(tmp_path: Path) -> None:
    limiter = RecordingLimiter()
    oversize = int(contracts().api["limits"]["rawRequestBytes"]) + 1
    sent, reads = await invoke_boundary(
        tmp_path,
        [(b"content-length", str(oversize).encode("ascii"))],
        [{"type": "http.request", "body": b"unused", "more_body": False}],
        limiter,
    )
    assert sent[0]["status"] == 413
    assert reads == 0
    assert limiter.begin_calls == 0
    assert limiter.finish_calls == 0


@pytest.mark.asyncio
async def test_rejected_start_does_not_release_another_request_owner(tmp_path: Path) -> None:
    limiter = RecordingLimiter("client_rate_limited")
    sent, reads = await invoke_boundary(
        tmp_path,
        [(b"content-length", b"4")],
        [{"type": "http.request", "body": b"test", "more_body": False}],
        limiter,
    )
    assert sent[0]["status"] == 429
    assert reads == 0
    assert limiter.begin_calls == 1
    assert limiter.finish_calls == 0


class _FakeCommandQueue:
    def __init__(self) -> None:
        self.closed = False
        self.joined = False

    def put_nowait(self, value: object) -> None:
        del value

    def close(self) -> None:
        self.closed = True

    def join_thread(self) -> None:
        self.joined = True


class _BlockingResultQueue:
    def __init__(self, entered: threading.Event) -> None:
        self.entered = entered
        self.closed = False
        self.joined = False

    def get(self, timeout: float) -> dict[str, object]:
        self.entered.set()
        time.sleep(timeout)
        raise queue.Empty

    def close(self) -> None:
        self.closed = True

    def join_thread(self) -> None:
        self.joined = True


class _FakeProcess:
    pid = 9876

    def __init__(self) -> None:
        self.alive = False

    def start(self) -> None:
        self.alive = True

    def is_alive(self) -> bool:
        return self.alive

    def join(self, timeout: float) -> None:
        del timeout

    def terminate(self) -> None:
        self.alive = False

    def kill(self) -> None:
        self.alive = False


class _FakeContext:
    def __init__(self, entered: threading.Event) -> None:
        self.entered = entered
        self.queue_count = 0
        self.queues: list[object] = []

    def Queue(self, maxsize: int) -> object:  # noqa: N802 - mirrors multiprocessing API
        del maxsize
        self.queue_count += 1
        if self.queue_count == 1:
            work_queue: object = _FakeCommandQueue()
        else:
            work_queue = _BlockingResultQueue(self.entered)
        self.queues.append(work_queue)
        return work_queue

    def Process(self, **values: object) -> _FakeProcess:  # noqa: N802
        del values
        return _FakeProcess()


def test_terminal_stop_prevents_late_replacement(tmp_path: Path) -> None:
    supervisor = WorkerSupervisor(tmp_path / "models")
    supervisor.stop()
    supervisor._schedule_replacement()
    time.sleep(0.05)
    assert supervisor.snapshot().child_pid is None
    assert supervisor.snapshot().restarts == 0


def test_stop_interrupts_replacement_warmup(tmp_path: Path) -> None:
    entered = threading.Event()
    supervisor = WorkerSupervisor(tmp_path / "models")
    supervisor._context = _FakeContext(entered)  # type: ignore[assignment]
    supervisor._schedule_replacement()
    assert entered.wait(timeout=1.0)
    started = time.monotonic()
    supervisor.stop(join_timeout=0.5)
    elapsed = time.monotonic() - started
    time.sleep(0.1)
    assert elapsed < 1.0
    assert supervisor.snapshot().child_pid is None
    assert not supervisor.ready
    assert not supervisor._replacement_threads
    assert all(work_queue.closed for work_queue in supervisor._context.queues)
    assert all(work_queue.joined for work_queue in supervisor._context.queues)
