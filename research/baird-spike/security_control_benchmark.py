from __future__ import annotations

import asyncio
import io
import json
import os
import threading
import time
import uuid
from pathlib import Path

import numpy as np
from PIL import Image
import starlette.formparsers as formparsers

import server
from runtime_asset_fixture import RuntimeAssetFixture


ROOT = Path(__file__).resolve().parent
BENCHMARK_SECRET = "security-control-secret"


def small_png_bytes():
    output = io.BytesIO()
    Image.new("RGB", (2, 2), color=(255, 255, 255)).save(output, format="PNG")
    return output.getvalue()


SMALL_PNG = small_png_bytes()


def asgi_scope(address, content_type, content_length=None):
    headers = [
        (b"host", b"testserver"),
        (b"content-type", content_type.encode("ascii")),
        (b"x-baird-benchmark", BENCHMARK_SECRET.encode("ascii")),
    ]
    if content_length is not None:
        headers.append((b"content-length", str(content_length).encode("ascii")))
    return {
        "type": "http",
        "asgi": {"version": "3.0", "spec_version": "2.3"},
        "http_version": "1.1",
        "method": "POST",
        "scheme": "http",
        "path": "/api/v1/verifications",
        "raw_path": b"/api/v1/verifications",
        "query_string": b"",
        "root_path": "",
        "headers": headers,
        "client": (address, 50000),
        "server": ("testserver", 80),
    }


def multipart_body(fields=None, files=None, boundary=None):
    boundary = boundary or f"baird-{uuid.uuid4().hex}"
    parts = []
    for name, value in fields or []:
        parts.append(
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"\r\n\r\n".encode("ascii")
            + value.encode("utf-8")
            + b"\r\n"
        )
    for name, filename, content_type, content in files or []:
        parts.append(
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"; filename=\"{filename}\"\r\n"
            f"Content-Type: {content_type}\r\n\r\n".encode("ascii")
            + content
            + b"\r\n"
        )
    parts.append(f"--{boundary}--\r\n".encode("ascii"))
    return boundary, b"".join(parts)


async def invoke(address, body, content_type, content_length="actual", chunk_size=None, chunk_delay=0.0, finish=True):
    messages = []
    tracker = {"receive_calls": 0}
    offset = 0
    delivered_final = False
    declared = len(body) if content_length == "actual" else content_length

    async def receive():
        nonlocal offset, delivered_final
        tracker["receive_calls"] += 1
        if chunk_delay:
            await asyncio.sleep(chunk_delay)
        if offset < len(body):
            size = chunk_size or len(body)
            chunk = body[offset:offset + size]
            offset += len(chunk)
            more_body = not finish or offset < len(body)
            return {"type": "http.request", "body": chunk, "more_body": more_body}
        if finish and not delivered_final:
            delivered_final = True
            return {"type": "http.request", "body": b"", "more_body": False}
        return {"type": "http.request", "body": b"", "more_body": True}

    async def send(message):
        messages.append(message)

    route_before = server.control_probe["route_entries"]
    decoder_before = server.control_probe["decoder_entries"]
    started = time.perf_counter()
    await server.app(asgi_scope(address, content_type, declared), receive, send)
    status = next(message["status"] for message in messages if message["type"] == "http.response.start")
    response_body = b"".join(message.get("body", b"") for message in messages if message["type"] == "http.response.body")
    payload = json.loads(response_body) if response_body else {}
    return {
        "status": status,
        "error": payload.get("error"),
        "result_free": "result" not in payload,
        "receive_calls": tracker["receive_calls"],
        "route_entries": server.control_probe["route_entries"] - route_before,
        "decoder_entries": server.control_probe["decoder_entries"] - decoder_before,
        "elapsed_ms": round((time.perf_counter() - started) * 1000, 2),
    }


def fake_worker_result(paths, _reference, _iteration, _force_hang=False):
    result = {
        "summary": "No differences found in checked fields",
        "fields": [],
        "panels": {"count": len(paths), "quality_scores": []},
        "human_only_limitations": [],
        "limitations": [],
    }
    return {
        "row": {
            "payload": {"result": result, "panel_boxes": []},
            "decode_preprocess_ms": 0,
            "ocr_ms": 0,
            "rules_serialize_ms": 0,
            "server_pipeline_ms": 0,
            "decoded_pixels": len(paths),
            "response_bytes": 0,
        },
        "worker_peak_rss_bytes": 0,
    }


def directory_bytes(path):
    total = 0
    for item in Path(path).rglob("*"):
        try:
            if item.is_file():
                total += item.stat().st_size
        except FileNotFoundError:
            pass
    return total


def request_dirs():
    return sorted(path.name for path in server.SPOOL_ROOT.glob("request-*") if path.is_dir())


def active_capacity_probe():
    controller = server.AdmissionController()
    simple_scope = lambda address: {"type": "http", "method": "POST", "headers": [], "client": (address, 50000)}
    first, first_status, _ = controller.acquire(simple_scope("192.0.2.11"))
    second, second_status, _ = controller.acquire(simple_scope("192.0.2.12"))
    third, third_status, third_code = controller.acquire(simple_scope("192.0.2.13"))
    observed = controller.inflight
    controller.release(first)
    controller.release(second)
    return {
        "first_status": first_status,
        "second_status": second_status,
        "third_token": third,
        "third_status": third_status,
        "third_code": third_code,
        "max_observed_inflight": observed,
        "passed": first_status is None and second_status is None and third_status == 503 and observed == server.MAX_ADMITTED_POSTS,
    }


def rate_probes():
    previous = os.environ.pop("BAIRD_BENCHMARK_SECRET", None)
    try:
        client_controller = server.AdmissionController()
        client_scope = {"type": "http", "method": "POST", "headers": [(b"x-baird-benchmark", b"not-authorized")], "client": ("192.0.2.21", 50000)}
        client_statuses = []
        for _ in range(server.MAX_CLIENT_STARTS_PER_TEN_MINUTES):
            token, status, _ = client_controller.acquire(client_scope)
            client_statuses.append(status)
            client_controller.release(token)
        _, client_final, client_code = client_controller.acquire(client_scope)

        global_controller = server.AdmissionController()
        global_statuses = []
        for index in range(server.MAX_GLOBAL_STARTS_PER_MINUTE):
            item_scope = {"type": "http", "method": "POST", "headers": [], "client": (f"198.51.100.{index + 1}", 50000)}
            token, status, _ = global_controller.acquire(item_scope)
            global_statuses.append(status)
            global_controller.release(token)
        final_scope = {"type": "http", "method": "POST", "headers": [], "client": ("203.0.113.1", 50000)}
        _, global_final, global_code = global_controller.acquire(final_scope)
    finally:
        if previous is not None:
            os.environ["BAIRD_BENCHMARK_SECRET"] = previous
    return {
        "client": {
            "allowed_starts": len(client_statuses),
            "final_status": client_final,
            "final_code": client_code,
            "unauthorized_bypass_header_ignored": client_final == 429,
            "passed": all(status is None for status in client_statuses) and client_final == 429,
        },
        "global": {
            "allowed_starts": len(global_statuses),
            "final_status": global_final,
            "final_code": global_code,
            "passed": all(status is None for status in global_statuses) and global_final == 503,
        },
    }


async def parser_limit_probes():
    reference = json.dumps({"brand": "TEST"})
    valid_file = ("files", "panel.png", "image/png", SMALL_PNG)
    cases = []

    async def run_case(name, fields, files, expected_status, expected_error, content_type=None, body_override=None, content_length="actual"):
        boundary, body = multipart_body(fields, files)
        result = await invoke(
            f"192.0.3.{len(cases) + 1}",
            body if body_override is None else body_override,
            content_type or f"multipart/form-data; boundary={boundary}",
            content_length=content_length,
            chunk_size=1024 * 1024,
        )
        result.update({
            "name": name,
            "expected_status": expected_status,
            "expected_error": expected_error,
            "passed": result["status"] == expected_status and result["error"] == expected_error,
        })
        cases.append(result)

    await run_case("zero_files", [("reference", reference)], [], 422, "invalid_panel_count")
    await run_case("six_files", [("reference", reference)], [valid_file] * 6, 200, None)
    await run_case("seven_files", [("reference", reference)], [valid_file] * 7, 413, "multipart_limit_exceeded")
    await run_case("many_tiny_files", [("reference", reference)], [valid_file] * 40, 413, "multipart_limit_exceeded")
    await run_case("extra_field", [("reference", reference), ("extra", "x")], [valid_file], 413, "multipart_limit_exceeded")
    await run_case("reference_over_32_kib", [("reference", "x" * (server.REFERENCE_LIMIT + 1))], [valid_file], 413, "multipart_limit_exceeded")
    await run_case("missing_boundary", [], [], 400, "invalid_multipart", content_type="multipart/form-data", body_override=b"x")
    await run_case("file_over_8_mib", [("reference", reference)], [("files", "large.jpg", "image/jpeg", b"x" * (server.PER_FILE_LIMIT + 1))], 413, "multipart_limit_exceeded")
    await run_case("aggregate_over_24_mib", [("reference", reference)], [("files", f"panel-{index}.jpg", "image/jpeg", b"x" * 6_300_000) for index in range(4)], 413, "multipart_limit_exceeded")

    boundary, small_body = multipart_body([("reference", reference)], [valid_file])
    fixed = await invoke("192.0.3.20", small_body, f"multipart/form-data; boundary={boundary}", content_length=server.RAW_REQUEST_LIMIT + 1)
    fixed.update({
        "name": "fixed_length_over_raw_limit",
        "expected_status": 413,
        "expected_error": "request_too_large",
        "passed": fixed["status"] == 413 and fixed["error"] == "request_too_large" and fixed["receive_calls"] == 0,
    })
    cases.append(fixed)

    long_name = "n" * 24_000 + ".jpg"
    overflow_boundary, overflow_body = multipart_body(
        [("reference", "x" * server.REFERENCE_LIMIT)],
        [("files", long_name, "image/jpeg", b"x" * (4 * 1024 * 1024)) for _ in range(6)],
    )
    if len(overflow_body) <= server.RAW_REQUEST_LIMIT:
        raise AssertionError("Raw overflow fixture did not exceed the configured envelope")
    for index, declared in enumerate((100, None), 21):
        overflow = await invoke(
            f"192.0.3.{index}",
            overflow_body,
            f"multipart/form-data; boundary={overflow_boundary}",
            content_length=declared,
            chunk_size=1024 * 1024,
        )
        overflow.update({
            "name": "understated_raw_overflow" if declared is not None else "absent_length_raw_overflow",
            "expected_status": 413,
            "expected_error": "request_too_large",
            "passed": overflow["status"] == 413 and overflow["error"] == "request_too_large" and overflow["route_entries"] == 0 and overflow["decoder_entries"] == 0,
        })
        cases.append(overflow)

    limit_failures_before_route = all(
        item["route_entries"] == 0 and item["decoder_entries"] == 0
        for item in cases
        if item["name"] != "six_files"
    )
    return {
        "cases": cases,
        "limit_failures_before_route": limit_failures_before_route,
        "passed": all(item["passed"] for item in cases) and limit_failures_before_route,
    }


async def slow_partial_multipart_probe():
    tracked_handles = []
    original_spooled = formparsers.SpooledTemporaryFile

    def tracked_spooled(*args, **kwargs):
        handle = original_spooled(*args, **kwargs)
        tracked_handles.append(handle)
        return handle

    formparsers.SpooledTemporaryFile = tracked_spooled
    baseline_bytes = directory_bytes(server.SPOOL_ROOT)
    baseline_dirs = request_dirs()
    boundary = "baird-slow-partial"
    prefix = (
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"files\"; filename=\"slow.jpg\"\r\n"
        "Content-Type: image/jpeg\r\n\r\n".encode("ascii")
    )
    body = prefix + (b"x" * (8 * 1024 * 1024))
    try:
        first = asyncio.create_task(invoke("192.0.4.1", body, f"multipart/form-data; boundary={boundary}", content_length=None, chunk_size=256 * 1024, chunk_delay=0.25, finish=False))
        second = asyncio.create_task(invoke("192.0.4.2", body, f"multipart/form-data; boundary={boundary}", content_length=None, chunk_size=256 * 1024, chunk_delay=0.25, finish=False))
        await asyncio.sleep(1.5)
        visible_during = directory_bytes(server.SPOOL_ROOT)
        third_boundary, third_body = multipart_body([("reference", "{}")], [("files", "panel.png", "image/png", SMALL_PNG)])
        third = await invoke("192.0.4.3", third_body, f"multipart/form-data; boundary={third_boundary}")
        first_result, second_result = await asyncio.gather(first, second)
    finally:
        formparsers.SpooledTemporaryFile = original_spooled
    final_bytes = directory_bytes(server.SPOOL_ROOT)
    final_dirs = request_dirs()
    rolled_handles = [handle for handle in tracked_handles if bool(getattr(handle, "_rolled", False))]
    recovery_boundary, recovery_body = multipart_body([("reference", json.dumps({"brand": "TEST"}))], [("files", "panel.png", "image/png", SMALL_PNG)])
    recovery = await invoke("192.0.4.4", recovery_body, f"multipart/form-data; boundary={recovery_boundary}")
    passed = all([
        first_result["status"] == 408,
        second_result["status"] == 408,
        first_result["result_free"],
        second_result["result_free"],
        third["status"] == 503,
        third["receive_calls"] == 0,
        bool(rolled_handles),
        all(handle.closed for handle in tracked_handles),
        visible_during > baseline_bytes,
        final_bytes == baseline_bytes,
        final_dirs == baseline_dirs,
        server.admission.inflight == 0,
        server.admission.spool_reserved == 0,
        recovery["status"] == 200,
    ])
    return {
        "deadline_seconds": server.UPLOAD_BODY_DEADLINE_SECONDS,
        "chunk_interval_ms": 250,
        "slow_client_results": [first_result, second_result],
        "third_while_slow": third,
        "tracked_handle_count": len(tracked_handles),
        "rolled_handle_count": len(rolled_handles),
        "all_handles_closed": all(handle.closed for handle in tracked_handles),
        "baseline_visible_bytes": baseline_bytes,
        "visible_bytes_during_partial_spool": visible_during,
        "final_visible_bytes": final_bytes,
        "baseline_request_dirs": baseline_dirs,
        "final_request_dirs": final_dirs,
        "recovery": recovery,
        "passed": passed,
    }


def large_png_bytes():
    pixels = np.random.default_rng(20260831).integers(0, 256, size=(1600, 1600, 3), dtype=np.uint8)
    output = io.BytesIO()
    Image.fromarray(pixels, mode="RGB").save(output, format="PNG", compress_level=0)
    return output.getvalue()


async def two_copy_full_stack_probe():
    content = large_png_bytes()
    if not 6_000_000 < len(content) < server.PER_FILE_LIMIT:
        raise AssertionError(f"Near-limit PNG size is outside the planned range: {len(content)}")
    reference = json.dumps({"brand": "TEST"})
    files = [("files", f"panel-{index}.png", "image/png", content) for index in range(1, 4)]
    boundary, body = multipart_body([("reference", reference)], files)
    if len(body) > server.RAW_REQUEST_LIMIT:
        raise AssertionError("Near-limit multipart fixture exceeds the raw request limit")
    lock = threading.Lock()
    release = threading.Event()
    both_owned = threading.Event()
    owner_count = 0
    original_verify = server.worker.verify

    def held_verify(paths, reference_value, iteration, force_hang=False):
        nonlocal owner_count
        with lock:
            owner_count += 1
            if owner_count == 2:
                both_owned.set()
        if not release.wait(10.0):
            raise TimeoutError("two-copy probe release timed out")
        return fake_worker_result(paths, reference_value, iteration, force_hang)

    baseline = directory_bytes(server.SPOOL_ROOT)
    server.worker.verify = held_verify
    try:
        first = asyncio.create_task(invoke("192.0.5.1", body, f"multipart/form-data; boundary={boundary}", chunk_size=1024 * 1024))
        second = asyncio.create_task(invoke("192.0.5.2", body, f"multipart/form-data; boundary={boundary}", chunk_size=1024 * 1024))
        reached = await asyncio.to_thread(both_owned.wait, 10.0)
        visible_peak = directory_bytes(server.SPOOL_ROOT)
        release.set()
        first_result, second_result = await asyncio.gather(first, second)
    finally:
        release.set()
        server.worker.verify = original_verify
    final_bytes = directory_bytes(server.SPOOL_ROOT)
    total_reserved = server.MAX_ADMITTED_POSTS * server.SPOOL_RESERVATION_PER_REQUEST
    return {
        "multipart_requests": 2,
        "files_per_request": 3,
        "file_bytes": len(content),
        "payload_per_request_bytes": len(content) * 3,
        "raw_body_per_request_bytes": len(body),
        "copy_factor_accounted": server.SPOOL_COPY_FACTOR,
        "reservation_per_request_bytes": server.SPOOL_RESERVATION_PER_REQUEST,
        "total_reserved_bytes": total_reserved,
        "spool_quota_bytes": server.SPOOL_QUOTA_BYTES,
        "both_requests_owned": reached,
        "baseline_visible_bytes": baseline,
        "peak_visible_bytes": visible_peak,
        "final_visible_bytes": final_bytes,
        "results": [first_result, second_result],
        "passed": all([
            reached,
            len(body) <= server.RAW_REQUEST_LIMIT,
            len(content) * 3 <= server.FILE_PAYLOAD_LIMIT,
            total_reserved <= server.SPOOL_QUOTA_BYTES,
            baseline < visible_peak <= baseline + total_reserved,
            final_bytes == baseline,
            first_result["status"] == 200,
            second_result["status"] == 200,
        ]),
    }


async def run_all():
    original_verify = server.worker.verify
    server.worker.verify = fake_worker_result
    try:
        rate_results = rate_probes()
        parser_limits = await parser_limit_probes()
        slow_partial = await slow_partial_multipart_probe()
        two_copy = await two_copy_full_stack_probe()
    finally:
        server.worker.verify = original_verify
    total_spool_reservation = server.MAX_ADMITTED_POSTS * server.SPOOL_RESERVATION_PER_REQUEST
    report = {
        "active_capacity": active_capacity_probe(),
        "client_rate": rate_results["client"],
        "global_rate": rate_results["global"],
        "real_app_parser_limits": parser_limits,
        "partial_multipart_deadline": slow_partial,
        "two_copy_full_stack": two_copy,
        "configured_limiter_key_cap": server.MAX_LIMITER_KEYS,
        "configured_limiter_key_ttl_seconds": server.LIMITER_KEY_TTL_SECONDS,
        "raw_request_reservation_bytes": server.MAX_ADMITTED_POSTS * server.RAW_REQUEST_LIMIT,
        "two_copy_spool_reservation_bytes": total_spool_reservation,
        "spool_quota_bytes": server.SPOOL_QUOTA_BYTES,
        "reservation_within_spool_quota": total_spool_reservation <= server.SPOOL_QUOTA_BYTES,
        "final_admission_inflight": server.admission.inflight,
        "final_spool_reserved": server.admission.spool_reserved,
        "final_request_dirs": request_dirs(),
    }
    report["passed"] = all([
        report["active_capacity"]["passed"],
        report["client_rate"]["passed"],
        report["global_rate"]["passed"],
        report["real_app_parser_limits"]["passed"],
        report["partial_multipart_deadline"]["passed"],
        report["two_copy_full_stack"]["passed"],
        report["reservation_within_spool_quota"],
        report["final_admission_inflight"] == 0,
        report["final_spool_reserved"] == 0,
        not report["final_request_dirs"],
    ])
    return report


def main():
    previous_environment = dict(os.environ)
    try:
        with RuntimeAssetFixture(readonly=True) as asset_environment:
            os.environ.update(asset_environment)
            os.environ["BAIRD_BENCHMARK_SECRET"] = BENCHMARK_SECRET

            async def execute():
                async with server.app.router.lifespan_context(server.app):
                    return await run_all()

            report = asyncio.run(execute())
    finally:
        os.environ.clear()
        os.environ.update(previous_environment)
    (ROOT / "results" / "security-control-evidence.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    if not report["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
