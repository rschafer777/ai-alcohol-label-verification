from __future__ import annotations

import json
import hashlib
import math
import os
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

import psutil
from playwright.sync_api import sync_playwright

import spike
import server
from runtime_asset_fixture import RuntimeAssetFixture, environment_with_assets


ROOT = Path(__file__).resolve().parent


def pctl(values, q):
    values = sorted(values)
    return values[max(0, math.ceil(len(values) * q) - 1)]


class TreePeakSampler:
    def __init__(self, pid):
        self.root = psutil.Process(pid)
        self.peak = 0
        self.stop = threading.Event()
        self.thread = threading.Thread(target=self.run, daemon=True)

    def run(self):
        while not self.stop.wait(0.01):
            try:
                processes = [self.root] + self.root.children(recursive=True)
                rss = sum(process.memory_info().rss for process in processes if process.is_running())
                self.peak = max(self.peak, rss)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

    def __enter__(self):
        self.thread.start()
        return self

    def __exit__(self, *args):
        self.stop.set()
        self.thread.join()


def wait_ready(url, timeout=20.0):
    deadline = time.perf_counter() + timeout
    while time.perf_counter() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=0.4) as response:
                payload = json.loads(response.read())
                if response.status == 200 and payload.get("ready"):
                    return payload
        except (urllib.error.URLError, TimeoutError, ConnectionError):
            pass
        time.sleep(0.05)
    raise TimeoutError("readiness endpoint did not become ready")


def startup_rejection_probe(port, creation_flags, environment, label):
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "server:app", "--host", "127.0.0.1", "--port", str(port), "--log-level", "warning"],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        env=environment,
        creationflags=creation_flags,
    )
    started = time.perf_counter()
    ready_observed = False
    try:
        deadline = started + 10.0
        while time.perf_counter() < deadline and process.poll() is None:
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/health/ready", timeout=0.25) as response:
                    ready_observed = ready_observed or response.status == 200
            except (urllib.error.URLError, TimeoutError, ConnectionError):
                pass
            time.sleep(0.05)
        return {
            "probe": label,
            "ready_observed": ready_observed,
            "process_exited": process.poll() is not None,
            "exit_code": process.poll(),
            "elapsed_ms": round((time.perf_counter() - started) * 1000, 2),
            "blocks_ready": not ready_observed and process.poll() not in (None, 0),
        }
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=3.0)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=3.0)


def main():
    cases = spike.make_cases()
    clean = next(case for case in cases if case["case_id"] == "S01_clean_one")
    records = []
    creation_flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    with RuntimeAssetFixture(readonly=True) as asset_environment:
        base_environment = environment_with_assets(asset_environment, PYTHONUNBUFFERED="1")
        invalid_registry_hash = startup_rejection_probe(8869, creation_flags, {**base_environment, "BAIRD_TEST_REGISTRY_HASH_OVERRIDE": "0" * 64}, "invalid_registry_hash")
        invalid_model_hash = startup_rejection_probe(8868, creation_flags, {**base_environment, "BAIRD_TEST_MODEL_HASH_OVERRIDE": "0" * 64}, "invalid_model_hash")
        invalid_rules_hash = startup_rejection_probe(8867, creation_flags, {**base_environment, "BAIRD_TEST_RULES_HASH_OVERRIDE": "0" * 64}, "invalid_rules_hash")
        missing_rules_environment = {**base_environment, "LABELVERIFY_REGULATORY_RULES_PATH": str(ROOT / "does-not-exist-regulatory-rules.json")}
        missing_rules = startup_rejection_probe(8866, creation_flags, missing_rules_environment, "missing_rules")
        with RuntimeAssetFixture(readonly=False) as writable_assets:
            writable_assets_probe = startup_rejection_probe(8865, creation_flags, environment_with_assets(writable_assets, PYTHONUNBUFFERED="1"), "writable_assets")
        with RuntimeAssetFixture(readonly=True) as wrong_version_assets:
            wrong_version_path = Path(wrong_version_assets["LABELVERIFY_REGULATORY_RULES_PATH"])
            wrong_version_path.chmod(0o600)
            wrong_version_payload = json.loads(wrong_version_path.read_text(encoding="utf-8"))
            wrong_version_payload["registry_version"] = "0.0.0-invalid"
            wrong_version_path.write_text(json.dumps(wrong_version_payload, indent=2), encoding="utf-8")
            wrong_version_path.chmod(0o400)
            wrong_version_hash = hashlib.sha256(wrong_version_path.read_bytes()).hexdigest()
            wrong_version_environment = environment_with_assets(
                wrong_version_assets,
                PYTHONUNBUFFERED="1",
                BAIRD_TEST_RULES_HASH_OVERRIDE=wrong_version_hash,
            )
            wrong_rules_version = startup_rejection_probe(8864, creation_flags, wrong_version_environment, "wrong_rules_version")
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(channel="chrome", headless=True)
            for iteration in range(1, 6):
                port = 8870 + iteration
                spawn_started = time.perf_counter()
                process = subprocess.Popen(
                    [sys.executable, "-m", "uvicorn", "server:app", "--host", "127.0.0.1", "--port", str(port), "--log-level", "warning"],
                    cwd=ROOT,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    env=base_environment,
                    creationflags=creation_flags,
                )
                with TreePeakSampler(process.pid) as peak:
                    try:
                        ready_payload = wait_ready(f"http://127.0.0.1:{port}/health/ready")
                        ready_ms = (time.perf_counter() - spawn_started) * 1000
                        page = browser.new_page(viewport={"width": 1440, "height": 1000})
                        page.goto(f"http://127.0.0.1:{port}", wait_until="networkidle")
                        page.evaluate("reference => window.reference = reference", clean["reference"])
                        page.set_input_files("#files", spike.case_paths(clean))
                        first_started = time.perf_counter()
                        with page.expect_response(lambda response: response.url.endswith("/api/v1/verifications"), timeout=15000) as response_info:
                            page.click("#verify")
                        response = response_info.value
                        payload = response.json()
                        page.wait_for_function("document.body.dataset.done === 'true'", timeout=15000)
                        first_wall_ms = (time.perf_counter() - first_started) * 1000
                        record = {
                            "iteration": iteration,
                            "process_spawn_to_ready_ms": round(ready_ms, 2),
                            "first_result_after_ready_wall_ms": round(first_wall_ms, 2),
                            "first_result_browser_visible_ms": round(float(page.get_attribute("body", "data-elapsed")), 2),
                            "process_spawn_to_first_complete_result_ms": round((time.perf_counter() - spawn_started) * 1000, 2),
                            "summary": payload["result"]["summary"],
                            "field_count": len(payload["result"]["fields"]),
                            "worker_reported_ready_ms": ready_payload["worker"]["worker_init_warmup_ms"],
                            "worker_pid": ready_payload["worker"]["worker_pid"],
                            "registry_sha256": ready_payload["worker"]["registry_sha256"],
                            "regulatory_rules_sha256": ready_payload["worker"]["regulatory_rules_sha256"],
                            "model_sha256": ready_payload["worker"]["model_sha256"],
                            "governed_assets_readonly": ready_payload["worker"]["governed_assets_readonly"],
                            "ocr_child_count": ready_payload["ocr_child_count"],
                            "http_status": response.status,
                        }
                        record["cold_submission_wait_plus_browser_visible_ms"] = round(
                            record["process_spawn_to_ready_ms"] + record["first_result_browser_visible_ms"], 2
                        )
                        records.append(record)
                        print(record, flush=True)
                        page.close()
                    finally:
                        process.terminate()
                        try:
                            process.wait(timeout=5.0)
                        except subprocess.TimeoutExpired:
                            process.kill()
                            process.wait(timeout=3.0)
                records[-1]["parent_child_peak_rss_bytes"] = peak.peak
            browser.close()
    report = {
        "runs": records,
        "invalid_registry_hash_probe": invalid_registry_hash,
        "invalid_model_hash_probe": invalid_model_hash,
        "invalid_rules_hash_probe": invalid_rules_hash,
        "missing_rules_probe": missing_rules,
        "wrong_rules_version_probe": wrong_rules_version,
        "writable_assets_probe": writable_assets_probe,
        "run_count": len(records),
        "clock_definition": "Process spawn before Python imports through ready, then first full browser result after ready",
        "all_complete_clean": all(record["summary"] == "No differences found in checked fields" and record["http_status"] == 200 for record in records),
        "all_runtime_hashes_verified": all(
            record["registry_sha256"] == server.EXPECTED_REGISTRY_HASH
            and record["regulatory_rules_sha256"] == server.EXPECTED_RULES_HASH
            and record["model_sha256"] == server.EXPECTED_MODEL_HASHES
            and record["governed_assets_readonly"] is True
            and record["ocr_child_count"] == 1
            for record in records
        ),
        "invalid_registry_hash_blocks_ready": invalid_registry_hash["blocks_ready"],
        "invalid_model_hash_blocks_ready": invalid_model_hash["blocks_ready"],
        "invalid_rules_hash_blocks_ready": invalid_rules_hash["blocks_ready"],
        "missing_rules_blocks_ready": missing_rules["blocks_ready"],
        "wrong_rules_version_blocks_ready": wrong_rules_version["blocks_ready"],
        "writable_assets_block_ready": writable_assets_probe["blocks_ready"],
        "max_process_spawn_to_ready_ms": max(record["process_spawn_to_ready_ms"] for record in records),
        "p95_cold_submission_wait_plus_browser_visible_ms": pctl([record["cold_submission_wait_plus_browser_visible_ms"] for record in records], 0.95),
        "max_cold_submission_wait_plus_browser_visible_ms": max(record["cold_submission_wait_plus_browser_visible_ms"] for record in records),
        "max_process_spawn_to_first_complete_result_ms": max(record["process_spawn_to_first_complete_result_ms"] for record in records),
        "max_parent_child_peak_rss_bytes": max(record["parent_child_peak_rss_bytes"] for record in records),
    }
    (ROOT / "results" / "cold-start-timings.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items() if key != "runs"}, indent=2))
    if not all([
        report["all_complete_clean"], report["all_runtime_hashes_verified"],
        report["invalid_registry_hash_blocks_ready"], report["invalid_model_hash_blocks_ready"],
        report["invalid_rules_hash_blocks_ready"], report["missing_rules_blocks_ready"],
        report["wrong_rules_version_blocks_ready"], report["writable_assets_block_ready"],
    ]):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
