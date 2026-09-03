from __future__ import annotations

from dataclasses import dataclass, field

from labelverify.contracts.models import CandidateSet, Evidence, OcrLine, PanelResult


@dataclass(frozen=True)
class WarningObservation:
    heading: str | None = None
    body: str | None = None
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

    def field(self, name: str) -> CandidateSet:
        return self.fields.get(name, CandidateSet(status="Not found"))
