"""Validate the production API against governed oracles and mutation controls."""

from __future__ import annotations

import argparse
import copy
import io
import json
import platform
import sys
import tempfile
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageFilter

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "backend"))
sys.path.insert(0, str(PROJECT_ROOT))

from labelverify.contracts.models import VerificationResult  # noqa: E402

from scripts import generate_fixture_corpus as fixture_generator  # noqa: E402
from scripts import validate_production_oracle as production_validator  # noqa: E402

DEFAULT_OUTPUT = Path("docs/08-validation/evidence/local-product-corpus.json")
DEFAULT_BUILD_ID = "vv-product-corpus-v1"

_BASE_COMPARE_RESULT = production_validator.compare_result


def classify_reason(row: dict[str, Any]) -> str:
    """Translate a production reason code into the independent oracle taxonomy."""

    code = str(row.get("reasonCode", ""))
    check_id = str(row.get("checkId", ""))
    if code == "numeric_match" and check_id == "net_contents":
        observed = str(row.get("observedDisplay", "")).casefold()
        reference = str(row.get("referenceDisplay", "")).casefold()
        observed_is_liters = " l" in observed or "liter" in observed or "litre" in observed
        reference_is_liters = " l" in reference or "liter" in reference or "litre" in reference
        if observed_is_liters != reference_is_liters:
            return "safe_equivalence"
    exact = {
        "exact_match",
        "reference_found_on_label",
        "warning_required_by_class",
        "warning_wording_words_exact",
        "proof_adjacent_to_abv",
        "wine_appellation_found",
        "numeric_match",
        "proof_abv_relationship_match",
        "proof_abv_relationship_and_placement_match",
        "safe_whitespace_match",
        "warning_required",
        "warning_not_required",
        "warning_wording_exact",
        "warning_heading_exact",
        "presentation_supported",
        "physical_size_and_density_supported",
        "panel_coverage_sufficient",
        "image_quality_sufficient",
        "beverage_type_supported",
        "field_of_vision_supported",
        "recognized_malt_class",
        "sulfite_declaration_found",
    }
    if code in exact:
        return "exact"
    if code in {"safe_representation_match", "reference_found_within_label_text"}:
        return "safe_equivalence"
    if code == "case_variation":
        return "case_variation"
    if code in {"punctuation_variation", "producer_formatting_variation"}:
        return "punctuation_variation"
    if code in {"ambiguous_candidates", "incomplete_plausible_designation"}:
        return "ambiguous"
    if code in {
        "beverage_type_uncertain",
        "ocr_near_match",
        "wine_brand_label_placement_review",
        "proof_distinction_requires_review",
    }:
        return "ambiguous"
    if code in {"ocr_wrap_punctuation_uncertain", "warning_punctuation_uncertain"}:
        return "punctuation_uncertainty"
    if code == "presentation_requires_review":
        if check_id in {"warning_separation", "warning_continuity"}:
            return "ambiguous"
        return "quality_degradation"
    if code in {
        "definite_difference",
        "numeric_difference",
        "warning_wording_difference",
        "warning_heading_case_or_punctuation",
        "presentation_failure",
        "physical_size_below_required",
    }:
        return "definite_difference"
    if code in {
        "field_of_vision_evidence_incomplete",
        "observed_not_found",
        "warning_not_found",
        "warning_heading_not_found",
        "sulfite_declaration_not_found",
        "wine_appellation_not_found",
    }:
        return "missing"
    if code == "malt_abv_optional_unless_added_alcohol":
        return "not_applicable"
    if code in {"observed_unreadable", "image_unreadable"}:
        return "unreadable"
    if code == "reliable_scale_unavailable":
        return "unsupported_measurement"
    if code.startswith("not_applicable"):
        return "not_applicable"
    if code == "image_quality_uncertain":
        return "quality_degradation"
    if code in {"panel_coverage_uncertain", "panel_coverage_absent"}:
        return "coverage_gap"
    return f"unclassified:{code or 'missing'}"


def compare_product_result(
    case_id: str,
    actual: dict[str, Any],
    oracle: dict[str, Any],
    ordered_check_ids: list[str],
) -> list[dict[str, Any]]:
    """Compare exact states and the oracle reason taxonomy for one result."""

    failures = _BASE_COMPARE_RESULT(case_id, actual, oracle, ordered_check_ids)
    expected_rows = oracle.get("checks")
    actual_rows = actual.get("checks")
    if not isinstance(expected_rows, list) or not isinstance(actual_rows, list):
        return failures
    for index, check_id in enumerate(ordered_check_ids):
        if index >= len(expected_rows) or index >= len(actual_rows):
            continue
        expected = expected_rows[index]
        observed = actual_rows[index]
        if expected.get("checkId") != check_id or observed.get("checkId") != check_id:
            continue
        expected_code = expected.get("reasonCode")
        if expected.get("state") != observed.get(
            "state"
        ) and production_validator._state_is_acceptable(expected, observed):
            continue
        if expected_code is not None:
            observed_value = observed.get("reasonCode")
            category = "reason_code"
        else:
            observed_value = classify_reason(observed)
            expected_code = expected.get("reasonClass")
            category = "reason_class"
        equivalent_match_classes = {"exact", "safe_equivalence"}
        reason_is_acceptable = observed_value == expected_code or (
            expected.get("state") == observed.get("state") == "Match"
            and expected_code in equivalent_match_classes
            and observed_value in equivalent_match_classes
        )
        if not reason_is_acceptable:
            failures.append(
                production_validator.failure(
                    case_id,
                    category,
                    expected_code,
                    {
                        "classifiedReason": observed_value,
                        "productionReasonCode": observed.get("reasonCode"),
                    },
                    check_id=check_id,
                    row_index=index,
                )
            )
    return failures


def result_semantics(body: dict[str, Any]) -> dict[str, tuple[Any, ...]]:
    semantics: dict[str, tuple[Any, ...]] = {}
    for row in body.get("checks", []):
        if not isinstance(row, dict) or not isinstance(row.get("checkId"), str):
            continue
        check_id = str(row["checkId"])
        state = row.get("state")
        reason_code = row.get("reasonCode")
        if (
            check_id == "warning_wording"
            and state in {"Match", "Review"}
            and reason_code
            in {
                "warning_wording_exact",
                "ocr_wrap_punctuation_uncertain",
                "warning_punctuation_uncertain",
            }
        ):
            state = "punctuation_supported_or_review"
        semantics[check_id] = (row.get("applicable"), state)
    return semantics


def request_payload(
    client: Any,
    reference: dict[str, Any],
    panels: list[tuple[str, bytes, str]],
) -> tuple[int, dict[str, Any], float]:
    files: list[tuple[str, tuple[Any, ...]]] = [
        ("reference", (None, json.dumps(reference), "application/json"))
    ]
    files.extend(("panels", panel) for panel in panels)
    started = time.perf_counter()
    response = client.post("/api/v1/verifications", files=files)
    duration_ms = round((time.perf_counter() - started) * 1000, 3)
    try:
        body = response.json()
    except json.JSONDecodeError:
        body = {"nonJsonBody": response.text[:200]}
    return response.status_code, body, duration_ms


def governed_case_payload(root: Path, case: dict[str, Any]) -> tuple[dict[str, Any], list[Any]]:
    reference = production_validator.load_json(
        production_validator.governed_path(root, case["referencePath"])
    )
    panels = []
    for panel in case.get("panels", []):
        path = production_validator.governed_path(root, panel["path"])
        panels.append((path.name, path.read_bytes(), str(panel["mimeType"])))
    return reference, panels


def render_mutated_panels(
    temporary_root: Path,
    spec: dict[str, Any],
    sections: list[str],
) -> list[tuple[str, bytes, str]]:
    panels = []
    for index, section in enumerate(sections, start=1):
        suffix = fixture_generator.extension_for(section)
        path = temporary_root / f"panel-{index}{suffix}"
        fixture_generator.render_panel(spec, section, path)
        panels.append((path.name, path.read_bytes(), fixture_generator.mime_for(section)))
    return panels


def mutate_payload(
    root: Path,
    temporary_root: Path,
    case: dict[str, Any],
    mutation: dict[str, Any],
    specs: dict[str, dict[str, Any]],
) -> tuple[dict[str, Any], list[tuple[str, bytes, str]]]:
    reference, panels = governed_case_payload(root, case)
    operation = mutation["operation"]
    target = mutation.get("target")
    value = mutation.get("value")
    spec = copy.deepcopy(specs[str(case["caseId"])])
    if operation == "rename_case_id":
        spec["caseId"] = value
    elif operation == "reverse_panels":
        panels.reverse()
    elif operation == "replace_reference_value":
        reference[str(target)] = value
    elif operation == "replace_label_text":
        visual_field = {
            "brand": "brand",
            "warning_heading_uppercase": "warningHeading",
        }.get(str(target))
        if visual_field is None:
            raise ValueError(f"Unsupported label target: {target}")
        spec["visual"][visual_field] = value
        panels = render_mutated_panels(temporary_root, spec, list(spec["panels"]))
    elif operation == "add_conflicting_candidate":
        if target != "country":
            raise ValueError(f"Unsupported conflicting candidate target: {target}")
        conflict_spec = copy.deepcopy(spec)
        conflict_spec["visual"]["conflictingCountry"] = value
        replacement = render_mutated_panels(temporary_root, conflict_spec, ["origin-conflict"])[0]
        panels[-1] = (panels[-1][0], replacement[1], replacement[2])
    elif operation == "remove_panel":
        matching = [index for index, section in enumerate(spec["panels"]) if section == target]
        if len(matching) != 1:
            raise ValueError(f"Expected one panel section named {target}")
        panels.pop(matching[0])
    elif operation == "apply_blur":
        blurred = []
        for filename, content, mime_type in panels:
            with Image.open(io.BytesIO(content)) as source:
                image = source.convert("RGB").filter(ImageFilter.GaussianBlur(radius=float(value)))
                output = io.BytesIO()
                image.save(output, format="PNG", compress_level=9, optimize=False)
            blurred.append((Path(filename).with_suffix(".png").name, output.getvalue(), mime_type))
        panels = blurred
    else:
        raise ValueError(f"Unsupported mutation operation: {operation}")
    return reference, panels


def execute_mutations(
    root: Path,
    client: Any,
    supervisor: Any,
    cases: list[dict[str, Any]],
    ordered_check_ids: list[str],
) -> list[dict[str, Any]]:
    case_map = {str(case["caseId"]): case for case in cases}
    plan = production_validator.load_json(root / "fixtures" / "mutations" / "mutation-plan-v1.json")
    specs = {str(spec["caseId"]): spec for spec in fixture_generator.case_specs()}
    baseline_cache: dict[str, tuple[int, dict[str, Any]]] = {}
    records = []
    with tempfile.TemporaryDirectory(prefix="labelverify-mutations-") as temporary:
        temporary_root = Path(temporary)
        for mutation in plan["mutations"]:
            mutation_id = str(mutation["mutationId"])
            source_id = str(mutation["sourceCaseId"])
            case = case_map[source_id]
            if source_id not in baseline_cache:
                if not supervisor.ready:
                    production_validator.wait_for_replacement(supervisor, 30.0)
                source_reference, source_panels = governed_case_payload(root, case)
                status, body, _ = request_payload(client, source_reference, source_panels)
                baseline_cache[source_id] = (status, body)
            baseline_status, baseline_body = baseline_cache[source_id]
            mutation_root = temporary_root / mutation_id
            mutation_root.mkdir(parents=True, exist_ok=True)
            failures = []
            baseline: dict[str, Any] | None = None
            if baseline_status == 200:
                try:
                    baseline = VerificationResult.model_validate(baseline_body).model_dump(
                        by_alias=True, mode="json"
                    )
                except Exception as exc:
                    failures.append(
                        production_validator.failure(
                            mutation_id,
                            "source_contract",
                            "valid VerificationResult",
                            f"{type(exc).__name__}: {exc}",
                        )
                    )
            else:
                failures.append(
                    production_validator.failure(
                        mutation_id,
                        "source_status",
                        200,
                        {
                            "httpStatus": baseline_status,
                            "code": baseline_body.get("code"),
                        },
                    )
                )
            if not supervisor.ready:
                production_validator.wait_for_replacement(supervisor, 30.0)
            try:
                reference, panels = mutate_payload(root, mutation_root, case, mutation, specs)
                status, body, duration_ms = request_payload(client, reference, panels)
            except Exception as exc:
                status = 0
                body = {}
                duration_ms = 0.0
                failures.append(
                    production_validator.failure(
                        mutation_id,
                        "mutation_execution",
                        "completed production request",
                        f"{type(exc).__name__}: {exc}",
                    )
                )
            observed_summary = body.get("summary") if isinstance(body, dict) else None
            actual_changed: list[str] = []
            check_count = 0
            observed_reasons: dict[str, str] = {}
            if status != 200:
                failures.append(
                    production_validator.failure(mutation_id, "http_status", 200, status)
                )
            else:
                try:
                    validated = VerificationResult.model_validate(body).model_dump(
                        by_alias=True, mode="json"
                    )
                    check_count = len(validated["checks"])
                    observed_summary = validated["summary"]
                    observed_reasons = {
                        row["checkId"]: row["reasonCode"] for row in validated["checks"]
                    }
                    baseline_semantics = result_semantics(baseline) if baseline else {}
                    mutated_semantics = result_semantics(validated)
                    if baseline is not None:
                        actual_changed = sorted(
                            check_id
                            for check_id in ordered_check_ids
                            if baseline_semantics.get(check_id) != mutated_semantics.get(check_id)
                        )
                    if check_count != 24:
                        failures.append(
                            production_validator.failure(
                                mutation_id, "check_count", 24, check_count
                            )
                        )
                except Exception as exc:
                    failures.append(
                        production_validator.failure(
                            mutation_id,
                            "result_contract",
                            "valid VerificationResult",
                            f"{type(exc).__name__}: {exc}",
                        )
                    )
            expected_changed = sorted(mutation["expectedChangedChecks"])
            if actual_changed != expected_changed:
                failures.append(
                    production_validator.failure(
                        mutation_id, "changed_checks", expected_changed, actual_changed
                    )
                )
            if observed_summary != mutation["expectedSummary"]:
                failures.append(
                    production_validator.failure(
                        mutation_id,
                        "summary",
                        mutation["expectedSummary"],
                        observed_summary,
                    )
                )
            record = {
                "mutationId": mutation_id,
                "sourceCaseId": source_id,
                "operation": mutation["operation"],
                "target": mutation.get("target"),
                "invariant": mutation["invariant"],
                "durationMs": duration_ms,
                "expectedSummary": mutation["expectedSummary"],
                "observedSummary": observed_summary,
                "expectedChangedChecks": expected_changed,
                "observedChangedChecks": actual_changed,
                "observedReasonCodes": observed_reasons,
                "checkCount": check_count,
                "failureCount": len(failures),
                "failures": failures,
                "pass": not failures,
            }
            records.append(record)
            marker = "PASS" if record["pass"] else "FAIL"
            print(f"mutation {mutation_id} {marker} {duration_ms} ms", flush=True)
    return records


def run_corpus_cases(
    root: Path,
    cases: list[dict[str, Any]],
    ordered_check_ids: list[str],
    worker_deadline: float,
    timeout_fault_deadline: float,
    readiness_timeout: float,
    build_id: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Run production cases in fresh rate-limit windows without bypassing limits."""

    records: list[dict[str, Any]] = []
    startups: list[dict[str, Any]] = []
    for offset in range(0, len(cases), 10):
        chunk_records, chunk_startups = production_validator.run_cases(
            root,
            cases[offset : offset + 10],
            ordered_check_ids,
            worker_deadline,
            timeout_fault_deadline,
            readiness_timeout,
            build_id,
        )
        records.extend(chunk_records)
        startups.extend(chunk_startups)
    return records, startups


def write_report(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run all production corpus cases and governed mutation controls."
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--build-id", default=DEFAULT_BUILD_ID)
    parser.add_argument("--readiness-timeout", type=float, default=30.0)
    parser.add_argument("--worker-deadline", type=float, default=15.0)
    parser.add_argument("--timeout-fault-deadline", type=float, default=0.001)
    args = parser.parse_args()
    if min(args.readiness_timeout, args.worker_deadline, args.timeout_fault_deadline) <= 0:
        parser.error("Timeout values must be positive")

    root = Path(__file__).resolve().parents[1]
    output = args.output if args.output.is_absolute() else root / args.output
    manifest = production_validator.load_json(root / "fixtures" / "corpus-manifest-v1.json")
    cases = manifest.get("cases", [])
    registry = production_validator.load_json(
        root / "contracts" / "selected-check-registry-v1.json"
    )
    ordered_check_ids = [row["checkId"] for row in registry["checks"]]
    fixture_errors, fixture_metrics = production_validator.validate_corpus(root)
    model_records, model_errors = production_validator.verify_model_assets(
        root / "models", root / "ops" / "model-manifest.json"
    )
    preflight_errors = fixture_errors + model_errors
    mutation_plan = production_validator.load_json(
        root / "fixtures" / "mutations" / "mutation-plan-v1.json"
    )
    if len(cases) != 30:
        preflight_errors.append(f"Expected 30 cases, found {len(cases)}")
    if sum(case.get("partition") == "development" for case in cases) != 24:
        preflight_errors.append("Expected exactly 24 development cases")
    if sum(case.get("partition") == "holdout" for case in cases) != 6:
        preflight_errors.append("Expected exactly 6 holdout cases")
    if len(ordered_check_ids) != 24:
        preflight_errors.append(f"Expected 24 checks, found {len(ordered_check_ids)}")
    if len(mutation_plan.get("mutations", [])) != 8:
        preflight_errors.append("Expected exactly 8 mutation controls")

    report: dict[str, Any] = {
        "schemaVersion": "1.0.0",
        "evidenceId": "T-032-B-LOCAL-PRODUCT-CORPUS",
        "createdAtUtc": datetime.now(UTC).isoformat(),
        "command": "uv run python scripts/validate_product_corpus.py",
        "environment": {
            "platform": platform.platform(),
            "python": platform.python_version(),
        },
        "snapshot": {
            **production_validator.report_hashes(root, [case["oraclePath"] for case in cases]),
            "validatorSha256": production_validator.sha256_file(Path(__file__)),
            "mutationPlanSha256": production_validator.sha256_file(
                root / "fixtures" / "mutations" / "mutation-plan-v1.json"
            ),
        },
        "preflight": {
            "pass": not preflight_errors,
            "errors": preflight_errors,
            "fixtureMetrics": fixture_metrics,
            "modelAssets": model_records,
        },
        "execution": {
            "serial": True,
            "worker": "labelverify.orchestration.supervisor.WorkerSupervisor",
            "workerDeadlineSeconds": args.worker_deadline,
            "controlledTimeoutDeadlineSeconds": args.timeout_fault_deadline,
            "cases": [],
            "mutations": [],
            "workerStartups": [],
        },
        "totals": {},
        "pass": False,
    }
    if preflight_errors:
        report["totals"] = {
            "manifestCases": len(cases),
            "attemptedCases": 0,
            "mutationControls": len(mutation_plan.get("mutations", [])),
            "attemptedMutations": 0,
            "failureCount": len(preflight_errors),
        }
        write_report(output, report)
        print(json.dumps({"output": str(output), "pass": False, "errors": preflight_errors}))
        return 1

    production_validator.compare_result = compare_product_result
    fatal_error = None
    case_records: list[dict[str, Any]] = []
    mutation_records: list[dict[str, Any]] = []
    startups: list[dict[str, Any]] = []
    try:
        case_records, startups = run_corpus_cases(
            root,
            cases,
            ordered_check_ids,
            args.worker_deadline,
            args.timeout_fault_deadline,
            args.readiness_timeout,
            args.build_id,
        )
        with production_validator.api_harness(
            root, args.build_id, args.worker_deadline, args.readiness_timeout
        ) as harness:
            client, supervisor, mutation_startup = harness
            startups.append(mutation_startup)
            mutation_records = execute_mutations(root, client, supervisor, cases, ordered_check_ids)
    except Exception as exc:
        fatal_error = f"{type(exc).__name__}: {exc}"

    report["execution"]["cases"] = case_records
    report["execution"]["mutations"] = mutation_records
    report["execution"]["workerStartups"] = startups
    if fatal_error:
        report["execution"]["fatalError"] = fatal_error
    case_failures = [item for record in case_records for item in record["failures"]]
    mutation_failures = [item for record in mutation_records for item in record["failures"]]
    false_clean_count = sum(bool(record["falseClean"]) for record in case_records)
    passed = (
        fatal_error is None
        and len(case_records) == 30
        and len(mutation_records) == 8
        and not case_failures
        and not mutation_failures
        and false_clean_count == 0
    )
    report["totals"] = {
        "manifestCases": 30,
        "attemptedCases": len(case_records),
        "passedCases": sum(bool(record["pass"]) for record in case_records),
        "failedCases": sum(not bool(record["pass"]) for record in case_records),
        "developmentCases": sum(record["partition"] == "development" for record in case_records),
        "holdoutCases": sum(record["partition"] == "holdout" for record in case_records),
        "expectedResultCheckRows": sum(
            int(record["expected"]["checkCount"]) for record in case_records
        ),
        "observedResultCheckRows": sum(
            int(record["observed"].get("checkCount", 0)) for record in case_records
        ),
        "mutationControls": 8,
        "attemptedMutations": len(mutation_records),
        "passedMutations": sum(bool(record["pass"]) for record in mutation_records),
        "failedMutations": sum(not bool(record["pass"]) for record in mutation_records),
        "falseCleanCount": false_clean_count,
        "failureCount": len(case_failures) + len(mutation_failures) + int(bool(fatal_error)),
    }
    report["pass"] = passed
    write_report(output, report)
    summary = {"output": str(output), "pass": passed, **report["totals"]}
    print(json.dumps(summary, indent=2))
    if case_failures or mutation_failures:
        print(json.dumps({"failures": case_failures + mutation_failures}, indent=2))
    if fatal_error:
        print(json.dumps({"fatalError": fatal_error}, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
