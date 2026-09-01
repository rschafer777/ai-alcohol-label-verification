from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_readme_performance_claims_match_decisive_evidence() -> None:
    evidence = json.loads(
        (ROOT / "docs/08-validation/evidence/local-performance.json").read_text(encoding="utf-8")
    )
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    warm_seconds = evidence["warm"]["p95WallMs"] / 1000
    cold_seconds = evidence["cold"]["p95ReadyThroughFirstResultMs"] / 1000

    assert f"Warm p95 was {warm_seconds:.3f} seconds" in readme
    assert f"Cold readiness through first result was {cold_seconds:.3f} seconds" in readme


def test_direct_container_command_supplies_healthcheck_host() -> None:
    dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "os.environ['LABELVERIFY_ALLOWED_HOST']" in dockerfile
    assert "--env LABELVERIFY_RUNTIME_MODE=direct" in readme
    assert "--env LABELVERIFY_ALLOWED_HOST=127.0.0.1:8080" in readme


def test_assertion_ledgers_use_release_archive_hashes() -> None:
    manifest = {}
    manifest_path = ROOT / "docs/10-release/RELEASE_MANIFEST.sha256"
    for line in manifest_path.read_text(encoding="utf-8").splitlines():
        digest, path = line.split("  ", maxsplit=1)
        manifest[path] = digest

    machine_ledger = json.loads(
        (
            ROOT / "docs/08-validation/evidence/assertion-evidence-ledger.json"
        ).read_text(encoding="utf-8")
    )
    compared_machine_artifacts = 0
    for assertion in machine_ledger["assertions"]:
        for artifact in assertion.get("artifacts", []):
            path = artifact["path"]
            if path in manifest:
                assert artifact["sha256"] == manifest[path], path
                compared_machine_artifacts += 1
    assert compared_machine_artifacts > 0

    human_ledger = (ROOT / "docs/08-validation/ASSERTION_EVIDENCE_LEDGER.md").read_text(
        encoding="utf-8"
    )
    rows = re.findall(
        r"^\| `(?P<path>[^`]+)` \|.*\| `(?P<digest>[0-9a-f]{64})` \|$",
        human_ledger,
        flags=re.MULTILINE,
    )
    compared_human_artifacts = 0
    for path, digest in rows:
        if path in manifest:
            assert digest == manifest[path], path
            compared_human_artifacts += 1
    assert compared_human_artifacts > 0
