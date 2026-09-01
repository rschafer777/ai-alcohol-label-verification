from __future__ import annotations

import json
import math
import os
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

import spike
from runtime_asset_fixture import RuntimeAssetFixture, environment_with_assets


ROOT = Path(__file__).resolve().parent
MANAGED_SERVER = "BAIRD_BASE_URL" not in os.environ
BASE_URL = os.environ.get("BAIRD_BASE_URL", "http://127.0.0.1:8765")
ITERATIONS = int(os.environ.get("BROWSER_ITERATIONS", "2"))
BENCHMARK_SECRET = os.environ.get("BAIRD_BENCHMARK_SECRET", "baird-managed-browser-secret")
manifest = json.loads((ROOT / "results" / "fixture-manifest.json").read_text(encoding="utf-8"))
case_filter = os.environ.get("BROWSER_CASES")
if case_filter:
    allowed_cases = {item.strip() for item in case_filter.split(",") if item.strip()}
    manifest = [case for case in manifest if case["case_id"] in allowed_cases]
runs = []
asset_fixture = None
server_process = None


def pctl(values, q):
    values = sorted(values)
    return values[max(0, math.ceil(len(values) * q) - 1)]


def wait_for_ready(page, wanted, timeout_seconds=20.0):
    deadline = time.perf_counter() + timeout_seconds
    observations = []
    while time.perf_counter() < deadline:
        response = page.request.get(f"{BASE_URL}/health/ready")
        payload = response.json()
        observations.append({"status": response.status, "ready": payload.get("ready")})
        if bool(payload.get("ready")) is wanted:
            return payload, observations
        time.sleep(0.05)
    raise TimeoutError(f"readiness did not become {wanted}")


def poll_health_until_stopped(stop, observations):
    while not stop.wait(0.05):
        try:
            with urllib.request.urlopen(f"{BASE_URL}/health/ready", timeout=0.4) as response:
                payload = json.loads(response.read())
                observations.append({"status": response.status, "ready": payload.get("ready")})
        except urllib.error.HTTPError as exc:
            payload = json.loads(exc.read())
            observations.append({"status": exc.code, "ready": payload.get("ready")})
        except (urllib.error.URLError, TimeoutError, ConnectionError):
            observations.append({"status": None, "ready": None})


def start_managed_server():
    global asset_fixture, server_process
    asset_fixture = RuntimeAssetFixture(readonly=True)
    asset_environment = asset_fixture.__enter__()
    environment = environment_with_assets(
        asset_environment,
        PYTHONUNBUFFERED="1",
        BAIRD_BENCHMARK_SECRET=BENCHMARK_SECRET,
    )
    creation_flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    server_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "server:app", "--host", "127.0.0.1", "--port", "8765", "--log-level", "warning"],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        env=environment,
        creationflags=creation_flags,
    )
    deadline = time.perf_counter() + 20.0
    while time.perf_counter() < deadline:
        if server_process.poll() is not None:
            raise RuntimeError("managed server exited before readiness")
        try:
            with urllib.request.urlopen(f"{BASE_URL}/health/ready", timeout=0.4) as response:
                if response.status == 200 and json.loads(response.read()).get("ready"):
                    return
        except (urllib.error.URLError, TimeoutError, ConnectionError):
            pass
        time.sleep(0.05)
    raise TimeoutError("managed server did not become ready")


def stop_managed_server():
    global asset_fixture, server_process
    if server_process and server_process.poll() is None:
        server_process.terminate()
        try:
            server_process.wait(timeout=5.0)
        except subprocess.TimeoutExpired:
            server_process.kill()
            server_process.wait(timeout=3.0)
    if asset_fixture:
        asset_fixture.__exit__()


if MANAGED_SERVER:
    start_managed_server()


with sync_playwright() as playwright:
    browser = playwright.chromium.launch(channel="chrome", headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 1000})
    page.goto(BASE_URL, wait_until="networkidle")
    page.evaluate("secret => window.benchmarkSecret = secret", BENCHMARK_SECRET)
    for case in manifest:
        page.evaluate("reference => window.reference = reference", case["reference"])
        expected_summary = case["expected_summary"]
        for iteration in range(1, ITERATIONS + 1):
            row = {"case_id": case["case_id"], "iteration": iteration, "panel_count": len(case["paths"]), "attempt_status": "started"}
            try:
                page.set_input_files("#files", spike.case_paths(case))
                with page.expect_response(lambda response: response.url.endswith("/api/v1/verifications"), timeout=9000) as response_info:
                    page.click("#verify")
                response = response_info.value
                payload = response.json()
                row["http_status"] = response.status
                row["cache_control"] = response.headers.get("cache-control")
                if response.status != 200:
                    row["attempt_status"] = "http_error"
                    row["error_payload"] = payload
                else:
                    page.wait_for_function("document.body.dataset.done === 'true'", timeout=9000)
                    result = payload["result"]
                    field_ids = {field["check_id"] for field in result["fields"]}
                    omitted = sorted(set(spike.ALL_CHECK_IDS) - field_ids)
                    unexpected = sorted(field_ids - set(spike.ALL_CHECK_IDS))
                    expected_summary, validation_errors = spike.validate_against_oracle(case["case_id"], result)
                    expected_fields = spike.expected_fields(case["case_id"])
                    actual_fields = {field["check_id"]: field for field in result["fields"]}
                    false_clean = int(
                        result["summary"] == "No differences found in checked fields"
                        and any(field["applicable"] and field["state"] != "Match" for field in result["fields"])
                    )
                    false_mismatch = sum(
                        1
                        for check_id, expected in expected_fields.items()
                        if expected["state"] != "Mismatch" and actual_fields.get(check_id, {}).get("state") == "Mismatch"
                    )
                    dom_rows = page.locator("#result tr[data-check-id]").count()
                    alternative_ui_errors = []
                    expected_country = expected_fields.get("country", {})
                    expected_alternatives = expected_country.get("expected_alternatives", [])
                    observed_alternatives = []
                    alternative_evidence = []
                    if expected_alternatives:
                        action_locator = page.locator("tr[data-check-id='country'] .evidence-action")
                        for action_index in range(action_locator.count()):
                            action = action_locator.nth(action_index)
                            value = action.get_attribute("data-value")
                            panel = action.get_attribute("data-panel")
                            polygon = action.get_attribute("data-polygon")
                            observed_alternatives.append(value)
                            alternative_evidence.append((panel, polygon))
                            action.click()
                            status_text = page.locator("#evidence-status").inner_text()
                            if value not in status_text or f"panel {panel}" not in status_text:
                                alternative_ui_errors.append(f"Evidence action did not focus {value!r} on panel {panel!r}")
                        if observed_alternatives != expected_alternatives:
                            alternative_ui_errors.append(
                                f"Expected alternative actions {expected_alternatives!r}, got {observed_alternatives!r}"
                            )
                        if len(alternative_evidence) != len(set(alternative_evidence)):
                            alternative_ui_errors.append("Alternative evidence actions do not identify distinct regions")
                    row.update({
                        "attempt_status": "complete",
                        "browser_visible_ms": round(float(page.get_attribute("body", "data-elapsed")), 2),
                        "server_ms": payload["server_ms"],
                        "worker_peak_rss_bytes": payload["worker_peak_rss_bytes"],
                        "response_bytes": payload["response_bytes"],
                        "summary": result["summary"],
                        "expected_summary": expected_summary,
                        "expected_correct": not validation_errors and not alternative_ui_errors and not omitted and not unexpected and dom_rows == len(spike.ALL_CHECK_IDS),
                        "field_validation_errors": validation_errors + alternative_ui_errors,
                        "field_mismatch_count": len(validation_errors) + len(alternative_ui_errors),
                        "missing_evidence_count": sum("evidence_ref" in error for error in validation_errors),
                        "false_clean_count": false_clean,
                        "false_mismatch_count": false_mismatch,
                        "field_count": len(result["fields"]),
                        "registry_check_count": len(spike.ALL_CHECK_IDS),
                        "omitted_active_checks": omitted,
                        "unexpected_checks": unexpected,
                        "dom_field_rows": dom_rows,
                        "status_text": page.locator("#status").inner_text(),
                        "limitations_count": page.locator("#limitations li").count(),
                        "alternative_action_values": observed_alternatives,
                        "alternative_action_evidence": alternative_evidence,
                    })
            except PlaywrightTimeoutError as exc:
                row.update({"attempt_status": "timeout", "error": str(exc)})
            except Exception as exc:
                row.update({"attempt_status": "assertion_error", "error": f"{type(exc).__name__}: {exc}"})
            runs.append(row)
            print(row, flush=True)

    ready_before, _ = wait_for_ready(page, True)
    old_pid = ready_before["worker"]["worker_pid"]
    clean = next(case for case in manifest if case["case_id"] == "S01_clean_one")
    forced_reference = dict(clean["reference"])
    forced_reference["_research_force_hang"] = True
    page.evaluate("reference => window.reference = reference", forced_reference)
    page.set_input_files("#files", spike.case_paths(clean))
    health_stop = threading.Event()
    health_observations = []
    health_thread = threading.Thread(target=poll_health_until_stopped, args=(health_stop, health_observations), daemon=True)
    health_thread.start()
    timeout_started = time.perf_counter()
    try:
        with page.expect_response(lambda response: response.url.endswith("/api/v1/verifications"), timeout=9000) as response_info:
            page.click("#verify")
        timeout_response = response_info.value
        timeout_payload = timeout_response.json()
        page.wait_for_function("document.body.dataset.done === 'true'", timeout=9000)
    except Exception:
        health_stop.set()
        health_thread.join(1.0)
        raise
    timeout_visible_ms = (time.perf_counter() - timeout_started) * 1000
    timeout_field_rows = page.locator("#result tr[data-check-id]").count()
    recovered_payload, recovery_observations = wait_for_ready(page, True, timeout_seconds=20.0)
    health_stop.set()
    health_thread.join(1.0)
    new_pid = recovered_payload["worker"]["worker_pid"]

    page.evaluate("reference => window.reference = reference", clean["reference"])
    page.set_input_files("#files", spike.case_paths(clean))
    with page.expect_response(lambda response: response.url.endswith("/api/v1/verifications"), timeout=9000) as response_info:
        page.click("#verify")
    recovery_response = response_info.value
    recovery_result = recovery_response.json().get("result", {})
    page.wait_for_function("document.body.dataset.done === 'true'", timeout=9000)
    timeout_recovery = {
        "forced_timeout_http_status": timeout_response.status,
        "forced_timeout_error": timeout_payload.get("error"),
        "forced_timeout_visible_ms": round(timeout_visible_ms, 2),
        "forced_timeout_field_rows": timeout_field_rows,
        "readiness_was_503": any(item["status"] == 503 and not item["ready"] for item in health_observations),
        "health_poll_observation_count": len(health_observations),
        "old_worker_pid": old_pid,
        "new_worker_pid": new_pid,
        "worker_pid_changed": old_pid != new_pid,
        "recovered_child_count": recovered_payload.get("ocr_child_count"),
        "recovery_http_status": recovery_response.status,
        "recovery_summary": recovery_result.get("summary"),
        "recovery_field_count": len(recovery_result.get("fields", [])),
        "recovery_observation_count": len(recovery_observations),
    }
    timeout_recovery["passed"] = all([
        timeout_recovery["forced_timeout_http_status"] == 504,
        timeout_recovery["forced_timeout_error"] == "inference_timeout",
        timeout_recovery["forced_timeout_visible_ms"] <= 6750,
        timeout_recovery["forced_timeout_field_rows"] == 0,
        timeout_recovery["readiness_was_503"],
        timeout_recovery["worker_pid_changed"],
        timeout_recovery["recovered_child_count"] == 1,
        timeout_recovery["recovery_http_status"] == 200,
        timeout_recovery["recovery_summary"] == "No differences found in checked fields",
        timeout_recovery["recovery_field_count"] == len(spike.ALL_CHECK_IDS),
    ])
    browser.close()

complete = [row for row in runs if row["attempt_status"] == "complete"]
times = [row["browser_visible_ms"] for row in complete]
report = {
    "runs": runs,
    "timeout_recovery": timeout_recovery,
    "browser": "Google Chrome stable headless via Playwright",
    "viewport": "1440x1000",
    "attempt_count": len(runs),
    "complete_count": len(complete),
    "completion_rate": len(complete) / len(runs),
    "timeout_count": sum(row["attempt_status"] == "timeout" for row in runs),
    "error_count": sum(row["attempt_status"] not in {"complete", "timeout"} for row in runs),
    "all_expected_correct": bool(complete) and all(row["expected_correct"] for row in complete),
    "field_validation_error_count": sum(row.get("field_mismatch_count", 0) for row in runs),
    "missing_evidence_count": sum(row.get("missing_evidence_count", 0) for row in runs),
    "false_clean_count": sum(row.get("false_clean_count", 0) for row in runs),
    "false_mismatch_count": sum(row.get("false_mismatch_count", 0) for row in runs),
    "p50_complete_ms": pctl(times, 0.50) if times else None,
    "p95_complete_ms": pctl(times, 0.95) if times else None,
    "max_complete_ms": max(times) if times else None,
    "managed_server": MANAGED_SERVER,
    "startup_asset_attestation": ready_before["worker"],
}
(ROOT / "results" / "browser-timings.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps({key: value for key, value in report.items() if key != "runs"}, indent=2))

stop_managed_server()

if report["completion_rate"] != 1.0 or not report["all_expected_correct"] or any([
    report["field_validation_error_count"], report["missing_evidence_count"],
    report["false_clean_count"], report["false_mismatch_count"],
]) or not timeout_recovery["passed"]:
    raise SystemExit(1)
