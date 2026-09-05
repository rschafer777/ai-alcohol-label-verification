from __future__ import annotations

from dataclasses import dataclass, field

from labelverify.contracts.models import CandidateSet, Evidence, OcrLine, PanelResult


@dataclass(frozen=True)
class WarningObservation:
    heading: str | None = None
    body: str | None = None
    # The read lines of the body in order: a word at the start or end of a line can be
    # cut by the edge of the photograph, a word inside a line cannot.
    body_lines: tuple[str, ...] = ()
    full_text: str | None = None
    heading_evidence: Evidence | None = None
    body_evidence: Evidence | None = None
    heading_bold: bool | None = None
    body_bold: bool | None = None
    separated: bool | None = None
    continuous: bool | None = None
    contrast_sufficient: bool | None = None
    legible: bool | None = None
    physical_size_mm: float | None = None
    characters_per_inch: float | None = None
    reliable_scale: bool = False
    scale_evidence: Evidence | None = None
    source_unreadable: bool = False


@dataclass(frozen=True)
class ObservedCandidates:
    fields: dict[str, CandidateSet]
    warning: WarningObservation
    panels: list[PanelResult]
    evidence: list[Evidence] = field(default_factory=list)
    # Every readable line, so a supplied application value can be located anywhere on the
    # label after extraction has chosen its own candidates.
    lines: list[OcrLine] = field(default_factory=list)
    # The statement as read on each further panel that carries it (a second photograph of
    # the same back label); the comparison keeps the best-read one and confirms words
    # across them.
    warning_alternates: list[WarningObservation] = field(default_factory=list)

    def field(self, name: str) -> CandidateSet:
        return self.fields.get(name, CandidateSet(status="Not found"))


def serialize_observed(observed: ObservedCandidates) -> dict[str, object]:
    """Serialize the complete post-extraction observation for governed revision reuse."""

    return {
        "fields": {
            key: value.model_dump(by_alias=True, mode="json")
            for key, value in observed.fields.items()
        },
        "warning": _serialize_warning(observed.warning),
        "panels": [item.model_dump(by_alias=True, mode="json") for item in observed.panels],
        "evidence": [item.model_dump(by_alias=True, mode="json") for item in observed.evidence],
        "lines": [item.model_dump(by_alias=True, mode="json") for item in observed.lines],
        "warningAlternates": [
            _serialize_warning(item) for item in observed.warning_alternates
        ],
    }


def deserialize_observed(value: dict[str, object]) -> ObservedCandidates:
    """Restore a persisted observation without invoking decode, preprocessing, or OCR."""

    fields_value = value.get("fields", {})
    if not isinstance(fields_value, dict):
        raise ValueError("Observation fields are invalid")
    return ObservedCandidates(
        fields={
            str(key): CandidateSet.model_validate(item)
            for key, item in fields_value.items()
        },
        warning=_deserialize_warning(value.get("warning")),
        panels=[PanelResult.model_validate(item) for item in _list(value.get("panels"))],
        evidence=[Evidence.model_validate(item) for item in _list(value.get("evidence"))],
        lines=[OcrLine.model_validate(item) for item in _list(value.get("lines"))],
        warning_alternates=[
            _deserialize_warning(item) for item in _list(value.get("warningAlternates"))
        ],
    )


def _serialize_warning(warning: WarningObservation) -> dict[str, object]:
    return {
        "heading": warning.heading,
        "body": warning.body,
        "bodyLines": list(warning.body_lines),
        "fullText": warning.full_text,
        "headingEvidence": _serialize_evidence(warning.heading_evidence),
        "bodyEvidence": _serialize_evidence(warning.body_evidence),
        "headingBold": warning.heading_bold,
        "bodyBold": warning.body_bold,
        "separated": warning.separated,
        "continuous": warning.continuous,
        "contrastSufficient": warning.contrast_sufficient,
        "legible": warning.legible,
        "physicalSizeMm": warning.physical_size_mm,
        "charactersPerInch": warning.characters_per_inch,
        "reliableScale": warning.reliable_scale,
        "scaleEvidence": _serialize_evidence(warning.scale_evidence),
        "sourceUnreadable": warning.source_unreadable,
    }


def _deserialize_warning(value: object) -> WarningObservation:
    if not isinstance(value, dict):
        raise ValueError("Warning observation is invalid")
    return WarningObservation(
        heading=_optional_str(value.get("heading")),
        body=_optional_str(value.get("body")),
        body_lines=tuple(str(item) for item in _list(value.get("bodyLines"))),
        full_text=_optional_str(value.get("fullText")),
        heading_evidence=_deserialize_evidence(value.get("headingEvidence")),
        body_evidence=_deserialize_evidence(value.get("bodyEvidence")),
        heading_bold=_optional_bool(value.get("headingBold")),
        body_bold=_optional_bool(value.get("bodyBold")),
        separated=_optional_bool(value.get("separated")),
        continuous=_optional_bool(value.get("continuous")),
        contrast_sufficient=_optional_bool(value.get("contrastSufficient")),
        legible=_optional_bool(value.get("legible")),
        physical_size_mm=_optional_float(value.get("physicalSizeMm")),
        characters_per_inch=_optional_float(value.get("charactersPerInch")),
        reliable_scale=bool(value.get("reliableScale", False)),
        scale_evidence=_deserialize_evidence(value.get("scaleEvidence")),
        source_unreadable=bool(value.get("sourceUnreadable", False)),
    )


def _serialize_evidence(value: Evidence | None) -> dict[str, object] | None:
    return None if value is None else value.model_dump(by_alias=True, mode="json")


def _deserialize_evidence(value: object) -> Evidence | None:
    return None if value is None else Evidence.model_validate(value)


def _list(value: object) -> list[object]:
    if not isinstance(value, list):
        return []
    return value


def _optional_str(value: object) -> str | None:
    return value if isinstance(value, str) else None


def _optional_bool(value: object) -> bool | None:
    return value if isinstance(value, bool) else None


def _optional_float(value: object) -> float | None:
    return float(value) if isinstance(value, (int, float)) else None
