from __future__ import annotations

import asyncio
import json
import os
import time
import uuid
from pathlib import Path

import server
import spike
from runtime_asset_fixture import RuntimeAssetFixture


ROOT = Path(__file__).resolve().parent


def multipart_body(case, reference):
    boundary = f"baird-{uuid.uuid4().hex}"
    parts = []
    parts.append(
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"reference\"\r\n\r\n"
        f"{json.dumps(reference)}\r\n".encode("utf-8")
    )
    for index, path in enumerate(spike.case_paths(case), 1):
        parts.append(
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"files\"; filename=\"panel-{index}.jpg\"\r\n"
            "Content-Type: image/jpeg\r\n\r\n".encode("ascii")
            + Path(path).read_bytes()
            + b"\r\n"
        )
    parts.append(f"--{boundary}--\r\n".encode("ascii"))
    return boundary, b"".join(parts)


async def invoke(address, body, boundary, tracker):
    delivered = False
    messages = []

    async def receive():
        nonlocal delivered
        tracker["receive_calls"] += 1
        if not delivered:
            delivered = True
            return {"type": "http.request", "body": body, "more_body": False}
        return {"type": "http.disconnect"}

    async def send(message):
        messages.append(message)

    scope = {
        "type": "http",
        "asgi": {"version": "3.0", "spec_version": "2.3"},
        "http_version": "1.1",
        "method": "POST",
        "scheme": "http",
        "path": "/api/v1/verifications",
        "raw_path": b"/api/v1/verifications",
        "query_string": b"",
        "root_path": "",
        "headers": [
            (b"host", b"testserver"),
            (b"content-type", f"multipart/form-data; boundary={boundary}".encode("ascii")),
            (b"content-length", str(len(body)).encode("ascii")),
            (b"x-baird-benchmark", b"runtime-control-secret"),
        ],
        "client": (address, 50000),
        "server": ("testserver", 80),
    }
    started = time.perf_counter()
    await server.app(scope, receive, send)
    status = next(message["status"] for message in messages if message["type"] == "http.response.start")
    response_body = b"".join(message.get("body", b"") for message in messages if message["type"] == "http.response.body")
    payload = json.loads(response_body) if response_body else None
    compact_payload = payload
    if payload and "result" in payload:
        compact_payload = {
            "summary": payload["result"].get("summary"),
            "field_count": len(payload["result"].get("fields", [])),
        }
    return {
        "status": status,
        "elapsed_ms": round((time.perf_counter() - started) * 1000, 2),
        "receive_calls": tracker["receive_calls"],
        "payload": compact_payload,
    }


async def wait_worker_ready(timeout=20.0):
    deadline = time.perf_counter() + timeout
    while time.perf_counter() < deadline:
        if server.worker.is_ready():
            return server.worker.ready_metadata
        await asyncio.sleep(0.05)
    raise TimeoutError("worker did not recover")


async def wait_worker_owned(timeout=3.0):
    deadline = time.perf_counter() + timeout
    while time.perf_counter() < deadline:
        if server.worker.verify_lock.locked():
            return
        await asyncio.sleep(0.01)
    raise TimeoutError("worker lock was not acquired")


def request_dirs():
    return sorted(path.name for path in server.SPOOL_ROOT.glob("request-*") if path.is_dir())


async def run_controls():
    cases = spike.make_cases()
    clean = next(case for case in cases if case["case_id"] == "S01_clean_one")
    clean_boundary, clean_body = multipart_body(clean, clean["reference"])
    hang_reference = dict(clean["reference"])
    hang_reference["_research_force_hang"] = True
    hang_boundary, hang_body = multipart_body(clean, hang_reference)
    initial_pid = server.worker.ready_metadata["worker_pid"]
    baseline_dirs = request_dirs()

    first_tracker = {"receive_calls": 0}
    first = asyncio.create_task(invoke("192.0.2.51", hang_body, hang_boundary, first_tracker))
    await wait_worker_owned()
    second_tracker = {"receive_calls": 0}
    second = asyncio.create_task(invoke("192.0.2.52", clean_body, clean_boundary, second_tracker))
    await asyncio.sleep(0.02)
    inflight_with_waiter = server.admission.inflight
    third_tracker = {"receive_calls": 0}
    third = asyncio.create_task(invoke("192.0.2.53", clean_body, clean_boundary, third_tracker))
    first_result, second_result, third_result = await asyncio.gather(first, second, third)
    recovered = await wait_worker_ready()
    recovery_tracker = {"receive_calls": 0}
    recovery_result = await invoke("192.0.2.54", clean_body, clean_boundary, recovery_tracker)
    after_queue_dirs = request_dirs()

    disconnect_tracker = {"receive_calls": 0}
    disconnected = asyncio.create_task(invoke("192.0.2.55", hang_body, hang_boundary, disconnect_tracker))
    await wait_worker_owned()
    disconnect_started = time.perf_counter()
    disconnected.cancel()
    await asyncio.sleep(0.05)
    disconnected.cancel()
    await asyncio.sleep(0.05)
    disconnected.cancel()
    disconnect_cancelled = False
    try:
        await disconnected
    except asyncio.CancelledError:
        disconnect_cancelled = True
    disconnect_completion_ms = round((time.perf_counter() - disconnect_started) * 1000, 2)
    final_ready = await wait_worker_ready()
    final_tracker = {"receive_calls": 0}
    final_recovery = await invoke("192.0.2.56", clean_body, clean_boundary, final_tracker)

    storm_tasks = []
    for index in range(8):
        tracker = {"receive_calls": 0}
        storm_tasks.append(asyncio.create_task(invoke(f"192.0.2.{70 + index}", clean_body, clean_boundary, tracker)))
        await asyncio.sleep(0.01)
    await wait_worker_owned()
    for _ in range(3):
        for task in storm_tasks:
            if not task.done():
                task.cancel()
        await asyncio.sleep(0.05)
    storm_outcomes = await asyncio.gather(*storm_tasks, return_exceptions=True)
    storm_cancelled = sum(isinstance(item, asyncio.CancelledError) for item in storm_outcomes)
    storm_statuses = [item["status"] for item in storm_outcomes if isinstance(item, dict)]
    storm_ready = await wait_worker_ready()
    storm_child_count = sum(1 for child in __import__("psutil").Process().children(recursive=False) if child.is_running())
    storm_dirs = request_dirs()
    post_storm_tracker = {"receive_calls": 0}
    post_storm_recovery = await invoke("192.0.2.90", clean_body, clean_boundary, post_storm_tracker)
    final_dirs = request_dirs()

    result = {
        "worker_queue_deadline_ms": round(server.WORKER_QUEUE_DEADLINE_SECONDS * 1000),
        "one_active_one_waiter_inflight": inflight_with_waiter,
        "active_hang": first_result,
        "waiting_request": second_result,
        "third_request": third_result,
        "third_rejected_before_receive": third_result["status"] == 503 and third_result["receive_calls"] == 0,
        "initial_worker_pid": initial_pid,
        "recovered_worker_pid": recovered["worker_pid"],
        "worker_replaced": initial_pid != recovered["worker_pid"],
        "recovery_request": recovery_result,
        "baseline_request_dirs": baseline_dirs,
        "request_dirs_after_queue_case": after_queue_dirs,
        "disconnect_cancelled": disconnect_cancelled,
        "disconnect_cancel_calls": 3,
        "disconnect_completion_ms": disconnect_completion_ms,
        "disconnect_worker_replaced": recovered["worker_pid"] != final_ready["worker_pid"],
        "final_recovery_request": final_recovery,
        "abort_storm_request_count": len(storm_tasks),
        "abort_storm_cancelled_count": storm_cancelled,
        "abort_storm_completed_statuses": storm_statuses,
        "abort_storm_ready_worker_pid": storm_ready["worker_pid"],
        "abort_storm_child_count": storm_child_count,
        "abort_storm_request_dirs": storm_dirs,
        "post_storm_recovery_request": post_storm_recovery,
        "final_request_dirs": final_dirs,
        "admission_inflight_final": server.admission.inflight,
        "spool_reserved_final": server.admission.spool_reserved,
    }
    result["passed"] = all([
        inflight_with_waiter == 2,
        first_result["status"] == 504,
        first_result["payload"].get("error") == "inference_timeout",
        second_result["status"] == 503,
        second_result["payload"].get("error") == "worker_queue_busy",
        second_result["elapsed_ms"] <= 1000,
        result["third_rejected_before_receive"],
        result["worker_replaced"],
        recovery_result["status"] == 200,
        recovery_result["payload"]["field_count"] == len(spike.ALL_CHECK_IDS),
        after_queue_dirs == baseline_dirs,
        disconnect_cancelled,
        disconnect_completion_ms >= server.WORKER_DEADLINE_SECONDS * 1000 - 250,
        result["disconnect_worker_replaced"],
        final_recovery["status"] == 200,
        storm_cancelled >= 1,
        all(status in {200, 503} for status in storm_statuses),
        storm_child_count == 1,
        storm_dirs == baseline_dirs,
        post_storm_recovery["status"] == 200,
        final_dirs == baseline_dirs,
        server.admission.inflight == 0,
        server.admission.spool_reserved == 0,
    ])
    return result


async def shutdown_ownership_probe():
    cases = spike.make_cases()
    clean = next(case for case in cases if case["case_id"] == "S01_clean_one")
    clean_boundary, clean_body = multipart_body(clean, clean["reference"])
    hang_reference = dict(clean["reference"])
    hang_reference["_research_force_hang"] = True
    hang_boundary, hang_body = multipart_body(clean, hang_reference)
    context = server.app.router.lifespan_context(server.app)
    await context.__aenter__()
    first_tracker = {"receive_calls": 0}
    second_tracker = {"receive_calls": 0}
    first = asyncio.create_task(invoke("192.0.2.101", hang_body, hang_boundary, first_tracker))
    await wait_worker_owned()
    second = asyncio.create_task(invoke("192.0.2.102", clean_body, clean_boundary, second_tracker))
    await asyncio.sleep(0.05)
    shutdown_started = time.perf_counter()
    await context.__aexit__(None, None, None)
    shutdown_ms = round((time.perf_counter() - shutdown_started) * 1000, 2)
    first_result, second_result = await asyncio.gather(first, second)
    child_count_after_shutdown = sum(1 for child in __import__("psutil").Process().children(recursive=False) if child.is_running())
    dirs_after_shutdown = request_dirs()
    inflight_after_shutdown = server.admission.inflight
    reserved_after_shutdown = server.admission.spool_reserved
    owned_jobs_after_shutdown = len(server.owned_worker_jobs)

    async with server.app.router.lifespan_context(server.app):
        recovery_tracker = {"receive_calls": 0}
        recovery = await invoke("192.0.2.103", clean_body, clean_boundary, recovery_tracker)
        recovered_child_count = sum(1 for child in __import__("psutil").Process().children(recursive=False) if child.is_running())

    result = {
        "shutdown_ms": shutdown_ms,
        "active_request": first_result,
        "waiting_request": second_result,
        "child_count_after_shutdown": child_count_after_shutdown,
        "request_dirs_after_shutdown": dirs_after_shutdown,
        "admission_inflight_after_shutdown": inflight_after_shutdown,
        "spool_reserved_after_shutdown": reserved_after_shutdown,
        "owned_jobs_after_shutdown": owned_jobs_after_shutdown,
        "recovery_request": recovery,
        "recovered_child_count": recovered_child_count,
    }
    result["passed"] = all([
        first_result["status"] == 504,
        second_result["status"] == 503,
        child_count_after_shutdown == 0,
        not dirs_after_shutdown,
        inflight_after_shutdown == 0,
        reserved_after_shutdown == 0,
        owned_jobs_after_shutdown == 0,
        recovery["status"] == 200,
        recovered_child_count == 1,
    ])
    return result


def main():
    previous_environment = dict(os.environ)
    try:
        with RuntimeAssetFixture(readonly=True) as asset_environment:
            os.environ.update(asset_environment)
            os.environ["BAIRD_BENCHMARK_SECRET"] = "runtime-control-secret"
            async def execute():
                async with server.app.router.lifespan_context(server.app):
                    controls = await run_controls()
                shutdown = await shutdown_ownership_probe()
                controls["shutdown_ownership"] = shutdown
                controls["passed"] = controls["passed"] and shutdown["passed"]
                return controls

            result = asyncio.run(execute())
    finally:
        os.environ.clear()
        os.environ.update(previous_environment)
    (ROOT / "results" / "runtime-control-evidence.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
