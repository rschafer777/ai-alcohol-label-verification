from __future__ import annotations

from dataclasses import dataclass

from labelverify.contracts.models import CheckResult, ReferenceRecord, SummaryState
from labelverify.domain.aggregation import aggregate, validate_check_set
from labelverify.domain.comparison import (
    _result,
    compare_abv,
    compare_class,
    compare_country,
    compare_net_contents,
    compare_producer,
    compare_proof,
    compare_text,
)
from labelverify.domain.types import ObservedCandidates
from labelverify.domain.warnings import warning_checks


@dataclass(frozen=True)
class ComparisonInputs:
    reference: ReferenceRecord
    observed: ObservedCandidates


def compare_all(inputs: ComparisonInputs) -> tuple[list[CheckResult], SummaryState]:
    reference = inputs.reference
    observed = inputs.observed
    checks = [
        compare_text("brand", "Brand name", reference.brand_name, observed.field("brand")),
        compare_class(reference.class_type, observed.field("class_type")),
        compare_abv(reference.abv_percent, observed.field("abv")),
        compare_proof(reference.proof, reference.abv_percent, observed.field("proof")),
        compare_net_contents(
            reference.net_contents_value,
            reference.net_contents_unit,
            observed.field("net_contents"),
        ),
        compare_producer(reference.producer_name_address, observed.field("producer")),
        compare_country(
            reference.is_imported, reference.country_of_origin, observed.field("country")
        ),
        *warning_checks(
            reference.abv_percent,
            observed.warning,
            reference.net_contents_value,
            reference.net_contents_unit,
        ),
        _panel_coverage(observed),
        _image_quality(observed),
    ]
    checks = _guard_degraded_evidence(checks, observed)
    validate_check_set(checks)
    return checks, aggregate(checks)


def _panel_coverage(observed: ObservedCandidates) -> CheckResult:
    panels = observed.panels
    if _appears_front_only(observed):
        return _result(
            "panel_coverage",
            "Panel coverage",
            "Not verified",
            "panel_coverage_uncertain",
            "The submitted panel appears to omit supplemental label elements",
        )
    if panels and all(item.coverage_state == "Sufficient" for item in panels):
        return _result(
            "panel_coverage",
            "Panel coverage",
            "Match",
            "panel_coverage_sufficient",
            "The submitted panels provide sufficient label coverage",
        )
    if panels:
        return _result(
            "panel_coverage",
            "Panel coverage",
            "Review",
            "panel_coverage_uncertain",
            "One or more panels may not provide complete label coverage",
        )
    return _result(
        "panel_coverage",
        "Panel coverage",
        "Not verified",
        "panel_coverage_absent",
        "No panel coverage evidence is available",
    )


def _image_quality(observed: ObservedCandidates) -> CheckResult:
    panels = observed.panels
    if not panels or any(item.coverage_state == "Unreadable" for item in panels):
        return _result(
            "image_quality",
            "Image quality",
            "Not verified",
            "image_unreadable",
            "One or more panels are unreadable and require replacement",
        )
    if any(item.coverage_state == "Review" for item in panels):
        return _result(
            "image_quality",
            "Image quality",
            "Review",
            "image_quality_uncertain",
            "One or more image-quality signals require review",
        )
    return _result(
        "image_quality",
        "Image quality",
        "Match",
        "image_quality_sufficient",
        "The image-quality signals support automated review",
    )


def _appears_front_only(observed: ObservedCandidates) -> bool:
    if len(observed.panels) != 1 or observed.panels[0].coverage_state != "Sufficient":
        return False
    core_fields = ("brand", "class_type", "abv", "proof", "net_contents")
    core_found = sum(
        observed.field(field).status in {"Found", "Ambiguous"} for field in core_fields
    )
    supplemental_found = any(
        observed.field(field).status in {"Found", "Ambiguous"}
        for field in ("producer", "country")
    ) or bool(observed.warning.full_text)
    return core_found >= 4 and not supplemental_found


def _guard_degraded_evidence(
    checks: list[CheckResult], observed: ObservedCandidates
) -> list[CheckResult]:
    evidence_panels = {item.evidence_id: item.panel_id for item in observed.evidence}
    panel_quality = {item.panel_id: item.coverage_state for item in observed.panels}
    guarded: list[CheckResult] = []
    for check in checks:
        if check.state != "Mismatch" or check.evidence_ref is None:
            guarded.append(check)
            continue
        quality = panel_quality.get(evidence_panels.get(check.evidence_ref, ""))
        if quality == "Unreadable":
            guarded.append(
                check.model_copy(
                    update={
                        "state": "Not verified",
                        "reason_code": "observed_unreadable",
                        "reason_text": (
                            "The supporting image is not readable enough to verify this field"
                        ),
                    }
                )
            )
        elif quality == "Review":
            guarded.append(
                check.model_copy(
                    update={
                        "state": "Review",
                        "reason_code": "quality_degraded_observation",
                        "reason_text": (
                            "The apparent difference comes from an image that requires review"
                        ),
                    }
                )
            )
        else:
            guarded.append(check)
    return guarded
