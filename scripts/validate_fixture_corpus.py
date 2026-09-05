"""Validate the independent fixture corpus and optional product result records."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

SUMMARY_CLEAN = "No differences found in checked fields"
SUMMARY_REVIEW = "Review needed"
SUMMARY_DIFFERENCE = "Differences detected"
VALID_STATES = {"Match", "Mismatch", "Review", "Not verified"}
VALID_EVIDENCE = {"required", "optional", "forbidden"}
REQUIRED_TAGS = {
    "exact",
    "safe_equivalence",
    "case_variation",
    "punctuation",
    "ambiguity",
    "mismatch",
    "missing",
    "warning",
    "image_quality",
    "panel_coverage",
    "invalid_image",
    "unsupported_media",
    "panel_count",
    "resource_boundary",
    "inference_timeout",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_governed_text(path: Path) -> str:
    """Hash governed text with LF line endings on every operating system."""
    payload = path.read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest()


def project_path(project_root: Path, relative: str) -> Path:
    candidate = (project_root / relative).resolve()
    fixtures_root = (project_root / "fixtures").resolve()
    if not candidate.is_relative_to(fixtures_root):
        raise ValueError(f"Fixture path escapes governed root: {relative}")
    return candidate


def expected_summary(checks: list[dict[str, Any]]) -> str:
    applicable = [row for row in checks if row["applicable"]]
    if any(row["state"] == "Mismatch" for row in applicable):
        return SUMMARY_DIFFERENCE
    if any(row["state"] in {"Review", "Not verified"} for row in applicable):
        return SUMMARY_REVIEW
    return SUMMARY_CLEAN


def validate_contracts(project_root: Path) -> tuple[list[str], dict[str, Any]]:
    errors: list[str] = []
    contracts_root = project_root / "contracts"
    api = load_json(contracts_root / "api-contract-v1.json")
    error_registry = load_json(contracts_root / "error-registry-v1.json")
    check_registry = load_json(contracts_root / "selected-check-registry-v1.json")
    regulatory = load_json(contracts_root / "regulatory-rules-v1.json")
    checks = [row["checkId"] for row in check_registry["checks"]]
    server_errors = [row["code"] for row in error_registry["errors"]]
    browser_errors = list(error_registry["browserOnly"])
    if len(checks) != 24 or len(set(checks)) != 24:
        errors.append("CG-001 selected-check registry is not 24 unique rows")
    if len(server_errors) != 27 or len(set(server_errors)) != 27:
        errors.append("CG-001 server error registry is not 27 unique rows")
    if len(browser_errors) != 4 or len(set(browser_errors)) != 4:
        errors.append("CG-001 browser error registry is not 4 unique rows")
    limits = api["limits"]
    expected_limits = {
        "rawRequestBytes": 13_631_488,
        "referenceBytes": 32_768,
        "fileBytes": 4_194_304,
        "aggregateFileBytes": 12_582_912,
        "groupingRequestBytes": 8_388_608,
        "panelCountMin": 1,
        "panelCountMax": 3,
        "pixelsPerImage": 12_000_000,
        "pixelsPerRequest": 36_000_000,
        "uploadDeadlineSeconds": 20,
        "serverDeadlineSeconds": 30,
        "browserDeadlineSeconds": 35,
        "workerDeadlineSeconds": 15.0,
    }
    if limits != expected_limits:
        errors.append("CG-001 request or runtime limits differ from the cleared values")
    return errors, {
        "api": api,
        "errorRegistry": error_registry,
        "checkRegistry": check_registry,
        "regulatory": regulatory,
        "checkIds": checks,
        "errorCodes": set(server_errors + browser_errors),
        "hashes": {
            path.name: sha256_governed_text(path)
            for path in sorted(contracts_root.glob("*-v1.json"), key=lambda item: item.name)
        },
    }


def validate_reference(reference: dict[str, Any], case_id: str) -> list[str]:
    errors: list[str] = []
    required = {
        "profileId",
        "brandName",
        "classType",
        "abvPercent",
        "netContentsValue",
        "netContentsUnit",
        "producerNameAddress",
        "isImported",
    }
    missing = required - set(reference)
    if missing:
        errors.append(f"{case_id}: reference misses {sorted(missing)}")
    if reference.get("profileId") != "all_beverages_demo_v2":
        errors.append(f"{case_id}: wrong profileId")
    if reference.get("beverageType") not in {"malt_beverage", "wine", "distilled_spirits"}:
        errors.append(f"{case_id}: wrong beverageType")
    if reference.get("referenceProvenance") not in {"sample", "manual", "manifest", "label_ocr"}:
        errors.append(f"{case_id}: wrong referenceProvenance")
    if reference.get("netContentsUnit") not in {"mL", "L", "fl oz", "pt", "qt", "gal"}:
        errors.append(f"{case_id}: unsupported net contents unit")
    if reference.get("isImported") and not reference.get("countryOfOrigin"):
        errors.append(f"{case_id}: imported reference has no country")
    if not reference.get("isImported") and reference.get("countryOfOrigin") is not None:
        errors.append(f"{case_id}: domestic reference contains country")
    return errors


def validate_oracle(
    oracle: dict[str, Any],
    case: dict[str, Any],
    check_ids: list[str],
    error_codes: set[str],
) -> list[str]:
    errors: list[str] = []
    case_id = case["caseId"]
    if oracle.get("caseId") != case_id:
        errors.append(f"{case_id}: oracle caseId mismatch")
    if oracle.get("authorship") != ("VV-LEAD independent of production comparison and aggregation"):
        errors.append(f"{case_id}: oracle authorship is missing")
    if oracle.get("outcomeKind") != case["expectedKind"]:
        errors.append(f"{case_id}: oracle outcome kind mismatch")
        return errors
    if case["expectedKind"] == "error":
        if "checks" in oracle or "summary" in oracle:
            errors.append(f"{case_id}: error oracle contains a partial result")
        error = oracle.get("error", {})
        if error.get("code") not in error_codes:
            errors.append(f"{case_id}: unknown expected error {error.get('code')}")
        if error.get("resultMustBeAbsent") is not True:
            errors.append(f"{case_id}: error does not require result absence")
        return errors
    checks = oracle.get("checks", [])
    actual_ids = [row.get("checkId") for row in checks]
    if actual_ids != check_ids:
        errors.append(f"{case_id}: oracle checks do not exactly follow the registry")
    for row in checks:
        check_id = row.get("checkId")
        if row.get("state") not in VALID_STATES:
            errors.append(f"{case_id}/{check_id}: invalid state")
        if row.get("evidence") not in VALID_EVIDENCE:
            errors.append(f"{case_id}/{check_id}: invalid evidence rule")
        if not isinstance(row.get("applicable"), bool):
            errors.append(f"{case_id}/{check_id}: applicable is not boolean")
        if not isinstance(row.get("mustAppear"), bool):
            errors.append(f"{case_id}/{check_id}: mustAppear is not boolean")
        if not row.get("applicable") and row.get("mustAppear"):
            errors.append(f"{case_id}/{check_id}: non-applicable row cannot be mandatory")
        if row.get("minimumAlternatives", 0) < 0:
            errors.append(f"{case_id}/{check_id}: negative alternative count")
    if oracle.get("summary") != expected_summary(checks):
        errors.append(f"{case_id}: authored summary violates independent precedence")
    return errors


def validate_holdout_seal(project_root: Path, manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    fixtures_root = project_root / "fixtures"
    seal_path = fixtures_root / "holdout" / "SEAL.sha256"
    if not seal_path.exists():
        return ["Holdout seal is missing"]
    sealed_paths: set[str] = set()
    for line in seal_path.read_text(encoding="ascii").splitlines():
        parts = line.split("  ", maxsplit=1)
        if len(parts) != 2:
            errors.append("Holdout seal has a malformed row")
            continue
        expected, relative = parts
        path = project_path(project_root, f"fixtures/{relative}")
        sealed_paths.add(relative)
        if not path.exists() or sha256(path) != expected:
            errors.append(f"Holdout seal mismatch: {relative}")
    required_paths: set[str] = set()
    for case in manifest["cases"]:
        if case["partition"] != "holdout":
            continue
        if not case["sealed"]:
            errors.append(f"{case['caseId']}: holdout is not marked sealed")
        required_paths.add(Path(case["referencePath"]).relative_to("fixtures").as_posix())
        required_paths.add(Path(case["oraclePath"]).relative_to("fixtures").as_posix())
        required_paths.add(f"holdout/cases/{case['caseId']}/case-manifest.json")
        for panel in case["panels"]:
            required_paths.add(Path(panel["path"]).relative_to("fixtures").as_posix())
    if required_paths != sealed_paths:
        missing = sorted(required_paths - sealed_paths)
        extra = sorted(sealed_paths - required_paths)
        errors.append(f"Holdout seal coverage differs: missing={missing}, extra={extra}")
    return errors


def validate_mutations(project_root: Path, case_ids: set[str], check_ids: set[str]) -> list[str]:
    errors: list[str] = []
    path = project_root / "fixtures" / "mutations" / "mutation-plan-v1.json"
    plan = load_json(path)
    rows = plan.get("mutations", [])
    ids = [row.get("mutationId") for row in rows]
    if len(rows) < 8 or len(ids) != len(set(ids)):
        errors.append("Mutation plan must contain at least 8 unique controls")
    for row in rows:
        mutation_id = row.get("mutationId")
        if row.get("sourceCaseId") not in case_ids:
            errors.append(f"{mutation_id}: unknown source case")
        changed = set(row.get("expectedChangedChecks", []))
        if not changed <= check_ids:
            errors.append(f"{mutation_id}: unknown expected changed check")
        if row.get("expectedSummary") not in {
            SUMMARY_CLEAN,
            SUMMARY_REVIEW,
            SUMMARY_DIFFERENCE,
        }:
            errors.append(f"{mutation_id}: invalid expected summary")
        if not row.get("invariant"):
            errors.append(f"{mutation_id}: invariant is missing")
    return errors


def scan_production_hardcoding(project_root: Path) -> list[str]:
    errors: list[str] = []
    patterns = [
        re.compile(r"\b[DH][0-9]{3}\b"),
        re.compile(r"fixtures[/\\]oracle", re.IGNORECASE),
        re.compile(r"corpus-oracle-index", re.IGNORECASE),
    ]
    roots = [project_root / "backend", project_root / "frontend" / "src"]
    suffixes = {".py", ".ts", ".tsx", ".js", ".jsx", ".json"}
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in suffixes:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            for pattern in patterns:
                if pattern.search(text):
                    errors.append(
                        f"Production hard-coding marker in {path.relative_to(project_root)}: "
                        f"{pattern.pattern}"
                    )
    return errors


def validate_sample(project_root: Path, contract_hashes: dict[str, str]) -> list[str]:
    errors: list[str] = []
    path = project_root / "fixtures" / "sample" / "sample-manifest-v1.json"
    sample = load_json(path)
    if sample.get("sampleContractVersion") != "1.0.0":
        errors.append("Sample contract version is not 1.0.0")
    if sample.get("syntheticOnly") is not True:
        errors.append("Sample is not marked synthetic-only")
    if sample.get("contractHashes") != contract_hashes:
        errors.append("Sample contract hashes differ from CG-001")
    reference_path = project_path(project_root, sample["referencePath"])
    if load_json(reference_path) != sample.get("reference"):
        errors.append("Sample inline reference differs from referencePath")
    panels = sample.get("panels", [])
    if len(panels) != 2:
        errors.append("Sample must contain exactly two governed panels")
    for panel in panels:
        panel_path = project_path(project_root, panel["path"])
        if not panel_path.exists() or sha256(panel_path) != panel.get("sha256"):
            errors.append(f"Sample panel hash mismatch: {panel.get('panelId')}")
    oracle_path = project_path(project_root, sample["oraclePath"])
    oracle = load_json(oracle_path)
    if sample.get("expectedSummary") not in {
        SUMMARY_CLEAN,
        SUMMARY_REVIEW,
        SUMMARY_DIFFERENCE,
    }:
        errors.append("Sample expected summary is not a supported deterministic result")
    elif oracle.get("summary") != sample.get("expectedSummary"):
        errors.append("Sample oracle differs from the declared expected summary")
    return errors


def validate_corpus(project_root: Path) -> tuple[list[str], dict[str, Any]]:
    errors, contracts = validate_contracts(project_root)
    manifest_path = project_root / "fixtures" / "corpus-manifest-v1.json"
    manifest = load_json(manifest_path)
    if manifest.get("schemaVersion") != "1.0.0":
        errors.append("Corpus schema version is not 1.0.0")
    if manifest.get("corpusId") != "labelverify-fixtures-v1":
        errors.append("Corpus ID is incorrect")
    if manifest.get("contractHashes") != contracts["hashes"]:
        errors.append("Corpus contract hashes differ from live CG-001")
    cases = manifest.get("cases", [])
    ids = [case.get("caseId") for case in cases]
    if len(cases) < 24 or len(ids) != len(set(ids)):
        errors.append("Corpus must contain at least 24 unique cases")
    development = [case for case in cases if case.get("partition") == "development"]
    holdout = [case for case in cases if case.get("partition") == "holdout"]
    if len(development) < 18 or manifest.get("developmentCount") != len(development):
        errors.append("Development count is below 18 or differs from the manifest")
    if len(holdout) < 6 or manifest.get("holdoutCount") != len(holdout):
        errors.append("Holdout count is below 6 or differs from the manifest")
    tags: set[str] = set()
    check_state_coverage: dict[str, set[str]] = {
        check_id: set() for check_id in contracts["checkIds"]
    }
    for case in cases:
        case_id = case["caseId"]
        tags.update(case.get("scenarioTags", []))
        reference_path = project_path(project_root, case["referencePath"])
        if not reference_path.exists():
            errors.append(f"{case_id}: reference file is missing")
        else:
            errors.extend(validate_reference(load_json(reference_path), case_id))
        panel_ids: set[str] = set()
        for panel in case.get("panels", []):
            panel_id = panel.get("panelId")
            if panel_id in panel_ids:
                errors.append(f"{case_id}: duplicate panelId {panel_id}")
            panel_ids.add(panel_id)
            panel_path = project_path(project_root, panel["path"])
            if not panel_path.exists():
                errors.append(f"{case_id}/{panel_id}: panel file is missing")
                continue
            if sha256(panel_path) != panel.get("sha256"):
                errors.append(f"{case_id}/{panel_id}: panel hash mismatch")
            if panel_path.stat().st_size != panel.get("bytes"):
                errors.append(f"{case_id}/{panel_id}: panel byte count mismatch")
        oracle_path = project_path(project_root, case["oraclePath"])
        if not oracle_path.exists():
            errors.append(f"{case_id}: oracle is missing")
            continue
        oracle = load_json(oracle_path)
        errors.extend(
            validate_oracle(
                oracle,
                case,
                contracts["checkIds"],
                contracts["errorCodes"],
            )
        )
        for row in oracle.get("checks", []):
            if row.get("applicable"):
                check_state_coverage[row["checkId"]].add(row["state"])
    missing_tags = REQUIRED_TAGS - tags
    if missing_tags:
        errors.append(f"Required scenario tags are missing: {sorted(missing_tags)}")
    uncovered = [check_id for check_id, states in check_state_coverage.items() if not states]
    if uncovered:
        errors.append(f"Selected checks without applicable oracle coverage: {uncovered}")
    errors.extend(validate_holdout_seal(project_root, manifest))
    errors.extend(validate_mutations(project_root, set(ids), set(contracts["checkIds"])))
    errors.extend(scan_production_hardcoding(project_root))
    errors.extend(validate_sample(project_root, contracts["hashes"]))
    metrics = {
        "totalCases": len(cases),
        "developmentCases": len(development),
        "holdoutCases": len(holdout),
        "selectedChecks": len(contracts["checkIds"]),
        "scenarioTags": len(tags),
        "mutationControls": len(
            load_json(project_root / "fixtures" / "mutations" / "mutation-plan-v1.json")[
                "mutations"
            ]
        ),
    }
    return errors, metrics


def validate_results(project_root: Path, results_path: Path) -> list[str]:
    errors: list[str] = []
    manifest = load_json(project_root / "fixtures" / "corpus-manifest-v1.json")
    case_map = {case["caseId"]: case for case in manifest["cases"]}
    payload = load_json(results_path)
    results = payload.get("results", []) if isinstance(payload, dict) else payload
    if not isinstance(results, list):
        return ["Result payload must be a list or an object with results"]
    seen: set[str] = set()
    for result in results:
        case_id = result.get("caseId")
        if case_id not in case_map:
            errors.append(f"Unknown result caseId: {case_id}")
            continue
        if case_id in seen:
            errors.append(f"Duplicate result caseId: {case_id}")
            continue
        seen.add(case_id)
        case = case_map[case_id]
        oracle = load_json(project_path(project_root, case["oraclePath"]))
        if oracle["outcomeKind"] == "error":
            if result.get("error", {}).get("code") != oracle["error"]["code"]:
                errors.append(f"{case_id}: wrong error code")
            if result.get("summary") is not None or result.get("checks"):
                errors.append(f"{case_id}: error result contains a partial result")
            continue
        if result.get("summary") != oracle["summary"]:
            errors.append(f"{case_id}: summary differs from independent oracle")
        actual_checks = result.get("checks", [])
        actual_map = {row.get("checkId"): row for row in actual_checks}
        if len(actual_map) != len(actual_checks):
            errors.append(f"{case_id}: duplicate result checks")
        for expected in oracle["checks"]:
            check_id = expected["checkId"]
            actual = actual_map.get(check_id)
            if expected["mustAppear"] and actual is None:
                errors.append(f"{case_id}/{check_id}: required result row is missing")
                continue
            if actual is None:
                continue
            if actual.get("state") != expected["state"]:
                errors.append(f"{case_id}/{check_id}: state differs from independent oracle")
            if expected["evidence"] == "required" and not actual.get("evidenceRef"):
                errors.append(f"{case_id}/{check_id}: required evidence is missing")
            if expected["evidence"] == "forbidden" and actual.get("evidenceRef"):
                errors.append(f"{case_id}/{check_id}: fabricated evidence is present")
            if len(actual.get("alternatives", [])) < expected["minimumAlternatives"]:
                errors.append(f"{case_id}/{check_id}: material alternatives are missing")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path)
    parser.add_argument("--results", type=Path)
    args = parser.parse_args()
    root = args.project_root.resolve() if args.project_root else Path(__file__).resolve().parents[1]
    errors, metrics = validate_corpus(root)
    if args.results:
        errors.extend(validate_results(root, args.results.resolve()))
    print(json.dumps({"errors": errors, "metrics": metrics, "pass": not errors}, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
