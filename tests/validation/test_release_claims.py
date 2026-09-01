from __future__ import annotations

import json
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
