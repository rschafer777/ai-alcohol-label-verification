from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_readme_matches_governed_limits_and_profile() -> None:
    api = json.loads((ROOT / "contracts/api-contract-v1.json").read_text(encoding="utf-8"))
    checks = json.loads(
        (ROOT / "contracts/selected-check-registry-v1.json").read_text(encoding="utf-8")
    )
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert api["limits"]["panelCountMax"] == 3
    assert api["$defs"]["Reference"]["properties"]["profileId"]["const"] == (
        "all_beverages_demo_v2"
    )
    assert len(checks["checks"]) == 24
    assert "one to three images" in readme
    assert "applies 24 deterministic" in readme
    assert "Malt beverages:" in readme
    assert "Wine:" in readme
    assert "Distilled spirits:" in readme
    assert "latest 500 results" in readme


def test_direct_container_command_supplies_healthcheck_host() -> None:
    dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "os.environ['LABELVERIFY_ALLOWED_HOST']" in dockerfile
    assert "--env LABELVERIFY_RUNTIME_MODE=direct" in readme
    assert "--env LABELVERIFY_ALLOWED_HOST=127.0.0.1:8080" in readme


def test_numbered_delivery_documents_are_present() -> None:
    required = [
        "docs/01-discovery/ASSIGNMENT_DISCOVERY_BASELINE.md",
        "docs/02-intake/INTAKE_REQUIREMENTS.md",
        "docs/03-baird/BAIRD.md",
        "docs/04-i2r-ae/ARCHITECTURE_ENGINEERING.md",
        "docs/05-frd/FEATURE_REQUIREMENTS.md",
        "docs/05-frd/TRACEABILITY_MATRIX.md",
        "docs/06-build-instructions/BUILD_INSTRUCTIONS.md",
        "docs/07-development/IMPLEMENTATION_RECORD.md",
        "docs/08-validation/VALIDATION_PROTOCOL.md",
        "docs/09-qa-qc-uat/QA_QC_UAT.md",
        "docs/10-release/RELEASE.md",
        "docs/11-federal-authorization-readiness/README.md",
    ]
    assert all((ROOT / path).is_file() for path in required)


def test_readme_documents_required_submission_material() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for heading in (
        "## Quick start on Windows",
        "## Run tests",
        "## Technology",
        "## Architecture",
        "## Assumptions",
        "## Trade-offs",
        "## Limitations",
    ):
        assert heading in readme
    assert not (ROOT / "LICENSE").exists()
    assert not (ROOT / "LICENSE.md").exists()
