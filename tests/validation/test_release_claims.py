from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _release_source_sha256(path: Path) -> str:
    payload = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(payload).hexdigest()


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
    assert "latest 500 product results" in readme


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


def test_baird_derived_requirement_ids_are_unique_and_sequential() -> None:
    baird = (ROOT / "docs/03-baird/BAIRD.md").read_text(encoding="utf-8")
    derived = baird.split("## Derived requirements", 1)[1].split(
        "## Feasibility assessment", 1
    )[0]
    identifiers = [int(value) for value in re.findall(r"(?m)^(\d+)\. ", derived)]
    assert identifiers == list(range(1, len(identifiers) + 1))


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


def test_product_holdout_is_sealed_balanced_and_evaluation_only() -> None:
    manifest_path = ROOT / "tests/validation/product-holdout-v1.json"
    seal = (ROOT / "tests/validation/product-holdout-v1.sha256").read_text(
        encoding="utf-8"
    ).split()[0]
    assert hashlib.sha256(manifest_path.read_bytes()).hexdigest() == seal
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    counts = {
        family: sum(product["beverageType"] == family for product in manifest["products"])
        for family in ("malt_beverage", "wine", "distilled_spirits")
    }
    assert counts == {"malt_beverage": 8, "wine": 8, "distilled_spirits": 8}
    assert len({product["productId"] for product in manifest["products"]}) == 24
    runtime_text = "\n".join(
        path.read_text(encoding="utf-8")
        for root in (ROOT / "backend/labelverify", ROOT / "frontend/src")
        for path in root.rglob("*")
        if path.suffix in {".py", ".ts", ".tsx"}
    )
    assert "product-holdout-v1" not in runtime_text


def test_ocr_promotion_evidence_enforces_zero_lost_correct_fields() -> None:
    evidence = json.loads(
        (ROOT / "docs/08-validation/evidence/ocr-bakeoff.json").read_text(
            encoding="utf-8"
        )
    )
    assert evidence["promotionGate"]["maximumLostCorrectWeakFields"] == 0
    for comparison in evidence["comparisons"].values():
        if comparison["weakFieldLosses"]:
            assert comparison["passesPromotionGate"] is False


def test_validation_evidence_binds_to_canonical_published_source_bytes() -> None:
    local = json.loads(
        (ROOT / "docs/08-validation/evidence/local-product-corpus.json").read_text(
            encoding="utf-8"
        )
    )["snapshot"]
    direct = {
        "validatorSha256": ROOT / "scripts/validate_product_corpus.py",
        "supervisorSha256": ROOT / "backend/labelverify/orchestration/supervisor.py",
        "pipelineSha256": ROOT / "backend/labelverify/orchestration/pipeline.py",
    }
    for key, path in direct.items():
        assert local[key] == _release_source_sha256(path)
    for relative, expected in local["productionSource"].items():
        assert expected == _release_source_sha256(ROOT / relative)

    private = json.loads(
        (ROOT / "docs/08-validation/evidence/private-uat-corpus-e2e.json").read_text(
            encoding="utf-8"
        )
    )["snapshot"]
    private_sources = {
        "validatorSha256": ROOT / "scripts/validate_private_uat_corpus_e2e.py",
        "supervisorSha256": ROOT / "backend/labelverify/orchestration/supervisor.py",
        "pipelineSha256": ROOT / "backend/labelverify/orchestration/pipeline.py",
    }
    for key, path in private_sources.items():
        assert private[key] == _release_source_sha256(path)
