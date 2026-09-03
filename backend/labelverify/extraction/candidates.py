from __future__ import annotations

import re
from collections.abc import Iterable
from difflib import SequenceMatcher

from labelverify.contracts.loader import contracts
from labelverify.contracts.models import (
    Candidate,
    CandidateSet,
    ConfidenceProvenance,
    Evidence,
    OcrLine,
    PanelResult,
    Point,
)
from labelverify.domain.normalize import casefolded, whitespace
from labelverify.domain.types import ObservedCandidates, WarningObservation

_PERCENT = re.compile(r"\b\d{1,3}(?:\.\d+)?\s*%", re.I)
_ABV_CONTEXT = re.compile(
    r"\b(?:alc(?:ohol)?\.?\s*(?:/|by)?\s*vol\.?|abv)\b",
    re.I,
)
_ALC_PREFIX = re.compile(r"\balc(?:ohol)?\.?\s*$", re.I)
_BY_VOL_SUFFIX = re.compile(r"^\s*(?:by\s*|/\s*)vol\.?\b", re.I)
_ALC_VOLUME_LOOSE = re.compile(r"\balc[a-z0-9]{0,10}.*\bvol(?:ume)?\b", re.I)
_PROOF = re.compile(r"\b\d{1,3}(?:\.\d+)?\s*proof\b", re.I)
_NET = re.compile(
    r"\b\d+(?:\.\d+)?\s*(?:fl\.?\s*(?:oz|0z)\.?|fluid\s+ounces?|pints?|pts?\.?|"
    r"quarts?|qts?\.?|gallons?|gals?\.?|ml|mL|L|liters?|litres?)\b",
    re.I,
)
_CLASS = re.compile(
    r"\b(?:bourbon|whisk(?:e)?y|vodka|gin|rum|tequila|brandy|liqueur|cordial|spirits?|"
    r"(?:grape\s*)?wine(?:\s*with)?|merlot|cabernet|chardonnay|pinot|riesling|ros[eé]|sauvignon|zinfandel|"
    r"syrah|shiraz|muscat|sangiovese|malbec|tempranillo|grenache|prosecco|"
    r"sangria|vermouth|port|sherry|champagne|sparkling\s+wine|"
    r"malt\s+beverage|beer|ale|lager|stout|porter|pilsner|ipa|india\s+pale\s+ale|"
    r"near\s+beer|cereal\s+beverage|hard\s+seltzer)\b",
    re.I,
)
_STRONG_CLASS = re.compile(
    r"\b(?:bourbon|whisk(?:e)?y|vodka|gin|rum|tequila|brandy|liqueur|cordial|"
    r"neutral\s+spirits?|grain\s+spirits?|distilled\s+spirits?|"
    r"(?:grape\s*)?wine(?:\s*with)?|merlot|cabernet|chardonnay|pinot|riesling|ros[eé]|sauvignon|zinfandel|"
    r"syrah|shiraz|muscat|sangiovese|malbec|tempranillo|grenache|prosecco|"
    r"sangria|vermouth|port|sherry|champagne|beer|ale|lager|"
    r"stout|porter|pilsner|india\s+pale\s+ale|near\s+beer|hard\s+seltzer)\b",
    re.I,
)
_PRODUCER_ROLE = re.compile(
    r"\b(?:bottled|distilled|produced|manufactured|blended|imported|packed|brewed|"
    r"canned|filled|vinted|cellared)\s*(?:(?:and|&)\s*"
    r"(?:bottled|canned|packed|filled)\s+)?by\b",
    re.I,
)
_PRODUCER_ENTITY = re.compile(
    r"\b(?:llc|l\.l\.c\.|inc\.?|corp\.?|corporation|ltd\.?|company|co\.?|imports?)\b",
    re.I,
)
_PRODUCER = re.compile(f"(?:{_PRODUCER_ROLE.pattern}|{_PRODUCER_ENTITY.pattern})", re.I)
_INDUSTRY_ORGANIZATION = re.compile(r"\b(?:brewery|brewing|winery|distillery)\b", re.I)
_COUNTRY = re.compile(
    r"\b(?:product\s+of|country\s+of\s+origin\s*:?|imported\s+from|hecho\s+en)\s+"
    r"([A-Za-z][A-Za-z .'-]{1,60})",
    re.I,
)
_WARNING = re.compile(r"government\s+warning\s*:?", re.I)
_APPELLATION = re.compile(
    r"\b(?:american|california|oregon|washington|new\s+york|napa\s+valley|sonoma|"
    r"willamette\s+valley|product\s+of\s+[A-Za-z][A-Za-z .'-]{1,60})\b",
    re.I,
)
_SULFITES = re.compile(r"\bcontains?\s+(?:sulfites?|a\s+sulfiting\s+agent)\b", re.I)
_WARNING_BODY_TERM = re.compile(
    r"\b(?:according|surgeon|general|women|should|drink|alcoholic|beverages|"
    r"pregnancy|risk|birth|defects|consumption|impairs|ability|drive|car|"
    r"operate|machinery|cause|health|problems)\b",
    re.I,
)
_WARNING_BODY_WORDS = {
    "according",
    "surgeon",
    "general",
    "women",
    "should",
    "drink",
    "alcoholic",
    "beverages",
    "during",
    "pregnancy",
    "because",
    "risk",
    "birth",
    "defects",
    "consumption",
    "impairs",
    "ability",
    "drive",
    "operate",
    "machinery",
    "cause",
    "health",
    "problems",
}
_SCALE = re.compile(r"\b(?:reference|synthetic)?\s*scale\s*:\s*(\d+(?:\.\d+)?)\s*mm\b", re.I)
_ADMINISTRATIVE = re.compile(
    r"\b(?:test\s+label|reference\s+scale|synthetic\s+scale|lot\s*:|"
    r"front\s*/?\s*brand\s+label|back\s+label)\b",
    re.I,
)
_NON_BRAND_CONTEXT = re.compile(
    r"(?:\bgovernment\s*warning|"
    r"\b(?:enjoy|drink)\s+responsibl[a-z]*\b|\bcertified\s+organic\b|"
    r"\bgluten\s+free\b|\b(?:ca\s*)?crv\b|\b(?:ia|me|vt)\s*ref\b|"
    r"\bproudly\s+crafted\s+in\b|(?:^|\b)[a-z]{0,2}arning\s*:|"
    r"\bdrink\b.{0,30}\bproud\b|\b[a-z]+\s+proud\b|"
    r"\bmore\s+flavou?r\b|\bmoref[a-z]{0,5}\b|"
    r"\bwithout\s+manners\b|"
    r"\bfrom\s+(?:certified\s+)?(?:organic\s+)?(?:sugar\s+cane|grapes?|grain|corn|fruit)\b|"
    r"\b(?:orange|lemon|lime|citrus)\s+peel\b|"
    r"\bhoney\s+and\s+spices?\b|"
    r"\bconta[a-z]{0,5}\s+sulf[a-z]*\b|"
    r"https?://|www\.|\.(?:com|org|net)\b)",
    re.I,
)
_INCOMPLETE_CLASS_CONTEXT = re.compile(
    r"\b(?:brewed|made|produced|distilled|flavored)\s+with\s*$", re.I
)
_REGISTRATION_CONTEXT = re.compile(
    r"\b(?:est\.?\s*(?:&|and)\s*reg\.?|permit|registry|lot\s*:?)\b", re.I
)
_PRODUCTION_DESCRIPTOR = re.compile(
    r"^(?:brewed|bottled|distilled|produced|manufactured|blended|packed|canned|"
    r"filled|vinted|cellared)(?:\s*(?:and|&)\s*"
    r"(?:brewed|bottled|distilled|produced|"
    r"packed|canned|filled))?(?:\s+by)?\s*:?$",
    re.I,
)
_WARNING_THRESHOLDS = contracts().rules["warning"]["visualDecisionThresholds"]


def locate_candidates(lines: list[OcrLine], panels: list[PanelResult]) -> ObservedCandidates:
    unreadable_panel_ids = {
        panel.panel_id for panel in panels if panel.coverage_state == "Unreadable"
    }
    ordered = sorted(
        (line for line in lines if line.panel_id not in unreadable_panel_ids),
        key=lambda item: item.reading_order,
    )
    factory = _EvidenceFactory()
    abv = _abv_candidates(ordered, factory)
    proof = _regex_candidates(ordered, _PROOF, "proof", factory)
    net = _regex_candidates(ordered, _NET, "net_contents", factory)
    class_type = _class_candidates(ordered, factory)
    producer = _producer_candidates(ordered, factory)
    country = _country_candidates(ordered, factory)
    appellation = _line_candidates(ordered, _APPELLATION, "wine_appellation", factory)
    sulfites = _line_candidates(ordered, _SULFITES, "wine_sulfites", factory)
    warning = _warning_observation(
        ordered,
        panels,
        factory,
        source_unreadable=bool(unreadable_panel_ids),
    )
    excluded = {
        item.reading_order
        for item in ordered
        if _line_has_abv(item.text)
        or _PROOF.search(item.text)
        or _NET.search(item.text)
        or _CLASS.search(item.text)
        or _PRODUCER_ROLE.search(item.text)
        or _COUNTRY.search(item.text)
        or _APPELLATION.search(item.text)
        or _WARNING.search(item.text)
        or _SULFITES.search(item.text)
        or _SCALE.search(item.text)
        or _ADMINISTRATIVE.search(item.text)
    }
    excluded.update(_warning_interruption_orders(ordered))
    excluded.update(_warning_body_orders(ordered))
    brand = _brand_candidates(ordered, excluded, factory)
    evidence = list(factory.evidence.values())
    fields = {
        "brand": brand,
        "class_type": class_type,
        "abv": abv,
        "proof": proof,
        "net_contents": net,
        "producer": producer,
        "country": country,
        "wine_appellation": appellation,
        "wine_sulfites": sulfites,
    }
    if unreadable_panel_ids:
        fields = {
            field: CandidateSet(status="Unreadable")
            if candidates.status == "Not found"
            else candidates
            for field, candidates in fields.items()
        }
    return ObservedCandidates(fields=fields, warning=warning, panels=panels, evidence=evidence)


class _EvidenceFactory:
    def __init__(self) -> None:
        self._sequence = 0
        self.evidence: dict[str, Evidence] = {}

    def from_line(self, role: str, line: OcrLine) -> Evidence:
        self._sequence += 1
        evidence_id = f"ev_{role}_{line.panel_id}_{self._sequence:02d}"
        value = Evidence(
            evidenceId=evidence_id,
            panelId=line.panel_id,
            polygonOriginalPixels=line.polygon,
            sourceView=line.source_view,
            transformId=line.transform_id,
            textSnippet=line.text,
            confidenceProvenance=ConfidenceProvenance(
                source="rapidocr",
                signal=line.confidence,
                calibratedProbability=False,
            ),
        )
        self.evidence[evidence_id] = value
        return value

    def from_lines(self, role: str, lines: list[OcrLine], text: str) -> Evidence:
        if not lines:
            raise ValueError("Combined evidence requires at least one OCR line")
        panel_id = lines[0].panel_id
        same_panel = [line for line in lines if line.panel_id == panel_id]
        xs = [point.x for line in same_panel for point in line.polygon]
        ys = [point.y for line in same_panel for point in line.polygon]
        polygon = [
            Point(x=min(xs), y=min(ys)),
            Point(x=max(xs), y=min(ys)),
            Point(x=max(xs), y=max(ys)),
            Point(x=min(xs), y=max(ys)),
        ]
        aggregate = OcrLine(
            panelId=panel_id,
            text=text,
            polygon=polygon,
            confidence=min(
                (line.confidence for line in same_panel if line.confidence is not None),
                default=None,
            ),
            readingOrder=min(line.reading_order for line in same_panel),
            sourceView="derived"
            if any(line.source_view == "derived" for line in same_panel)
            else "original",
            transformId=same_panel[0].transform_id,
        )
        return self.from_line(role, aggregate)


def _candidate_set(items: list[Candidate]) -> CandidateSet:
    # Multiple OCR views can produce different readings for the same physical
    # line. One region is one piece of evidence, so retain only its strongest
    # reading before deciding whether independently located values conflict.
    by_region: dict[tuple[str, tuple[tuple[int, int], ...]], Candidate] = {}
    for item in items:
        region_key = (
            item.evidence.panel_id,
            tuple((point.x, point.y) for point in item.evidence.polygon_original_pixels),
        )
        current = by_region.get(region_key)
        if current is None or (item.evidence.confidence_provenance.signal or 0) > (
            current.evidence.confidence_provenance.signal or 0
        ):
            by_region[region_key] = item

    unique: dict[str, Candidate] = {}
    for item in by_region.values():
        key = casefolded(item.value)
        current = unique.get(key)
        if current is None or (item.evidence.confidence_provenance.signal or 0) > (
            current.evidence.confidence_provenance.signal or 0
        ):
            unique[key] = item
    values = list(unique.values())
    if not values:
        return CandidateSet(status="Not found")
    if len(values) == 1:
        return CandidateSet(status="Found", candidates=values)
    return CandidateSet(status="Ambiguous", candidates=values)


def _regex_candidates(
    lines: Iterable[OcrLine], pattern: re.Pattern[str], role: str, factory: _EvidenceFactory
) -> CandidateSet:
    items: list[Candidate] = []
    for line in lines:
        for match in pattern.finditer(line.text):
            items.append(Candidate(value=match.group(0), evidence=factory.from_line(role, line)))
    return _candidate_set(items)


def _abv_candidates(lines: Iterable[OcrLine], factory: _EvidenceFactory) -> CandidateSet:
    items: list[Candidate] = []
    for line in lines:
        percentages = list(_PERCENT.finditer(line.text))
        contexts = list(_ABV_CONTEXT.finditer(line.text))
        for match in percentages:
            standalone = re.fullmatch(r"\s*\d{1,3}(?:\.\d+)?\s*%\s*", line.text) is not None
            contextual = _percent_has_abv_context(line.text, match, contexts)
            if standalone or contextual:
                items.append(
                    Candidate(value=match.group(0), evidence=factory.from_line("abv", line))
                )
    return _candidate_set(items)


def _line_has_abv(value: str) -> bool:
    percentages = list(_PERCENT.finditer(value))
    if not percentages:
        return False
    contexts = list(_ABV_CONTEXT.finditer(value))
    if re.fullmatch(r"\s*\d{1,3}(?:\.\d+)?\s*%\s*", value):
        return True
    return any(_percent_has_abv_context(value, percent, contexts) for percent in percentages)


def _percent_has_abv_context(
    value: str, percent: re.Match[str], contexts: list[re.Match[str]]
) -> bool:
    if any(
        min(abs(percent.end() - context.start()), abs(context.end() - percent.start())) <= 18
        for context in contexts
    ):
        return True
    if _ALC_VOLUME_LOOSE.search(value):
        return True
    before = value[max(0, percent.start() - 20) : percent.start()]
    after = value[percent.end() : percent.end() + 20]
    return bool(_BY_VOL_SUFFIX.search(after) or _ALC_PREFIX.search(before))


def _line_candidates(
    lines: Iterable[OcrLine], pattern: re.Pattern[str], role: str, factory: _EvidenceFactory
) -> CandidateSet:
    return _candidate_set(
        [
            Candidate(value=whitespace(line.text), evidence=factory.from_line(role, line))
            for line in lines
            if pattern.search(line.text)
        ]
    )


def _class_candidates(lines: list[OcrLine], factory: _EvidenceFactory) -> CandidateSet:
    matched = [line for line in lines if _CLASS.search(line.text)]
    strong = [line for line in matched if _STRONG_CLASS.search(line.text)]
    preferred = [
        line
        for line in strong
        if not _line_has_abv(line.text)
        and not _NET.search(line.text)
        and not _PROOF.search(line.text)
        and not _PRODUCER.search(line.text)
        and not _COUNTRY.search(line.text)
    ]
    selected = preferred or strong or matched
    complete = [line for line in selected if not _INCOMPLETE_CLASS_CONTEXT.search(line.text)]
    if complete:
        selected = complete
    return _line_candidates(selected, _CLASS, "class_type", factory)


def _producer_candidates(lines: list[OcrLine], factory: _EvidenceFactory) -> CandidateSet:
    items: list[Candidate] = []
    for index, line in enumerate(lines):
        following = lines[index + 1 : index + 7]
        industry_with_location = bool(
            _INDUSTRY_ORGANIZATION.search(line.text)
            and _industry_location_is_connected(line, following)
        )
        if not _PRODUCER.search(line.text) and not industry_with_location:
            continue
        group = [line]
        if _US_STATE_CODE.search(line.text) or re.search(
            r"\b(?:u\.?s\.?a\.?|united\s+states)\b", line.text, re.I
        ):
            following = []
        for next_line in following:
            if next_line.panel_id != line.panel_id or not _same_column(line, next_line):
                continue
            if (
                _REGISTRATION_CONTEXT.search(next_line.text)
                or _NON_BRAND_CONTEXT.search(next_line.text)
                or _looks_like_warning_body_text(next_line.text)
            ):
                break
            if any(_same_normalized_line(next_line.text, item.text) for item in group):
                continue
            if _line_has_abv(next_line.text) or any(
                pattern.search(next_line.text) for pattern in (_WARNING, _PROOF, _NET, _CLASS)
            ):
                break
            group.append(next_line)
            if _looks_like_domestic_location(next_line.text):
                break
        text = whitespace(" ".join(item.text for item in group))
        items.append(Candidate(value=text, evidence=factory.from_lines("producer", group, text)))
    items = [item for item in items if _producer_is_structured(item.value)]
    items = _drop_contained_candidates(items)
    return _candidate_set(items)


def _country_candidates(lines: list[OcrLine], factory: _EvidenceFactory) -> CandidateSet:
    items: list[Candidate] = []
    for line in lines:
        match = _COUNTRY.search(line.text)
        if match:
            items.append(
                Candidate(
                    value=whitespace(match.group(1)).rstrip(" .,:;"),
                    evidence=factory.from_line("country", line),
                )
            )
    return _candidate_set(items)


def _brand_candidates(
    lines: list[OcrLine], excluded: set[int], factory: _EvidenceFactory
) -> CandidateSet:
    eligible = [
        line
        for line in lines
        if line.reading_order not in excluded
        and 2 <= len(whitespace(line.text)) <= 160
        and any(character.isalpha() for character in line.text)
        and (line.confidence or 0) >= 0.60
        and re.match(r"^\s*&", line.text) is None
        and not _ADMINISTRATIVE.search(line.text)
        and not _NON_BRAND_CONTEXT.search(line.text)
        and not _looks_like_domestic_location(line.text)
        and not _PRODUCTION_DESCRIPTOR.fullmatch(whitespace(line.text))
        and re.match(r"^\s*\d+(?:\.\d+)?\s*%", line.text) is None
        and not _looks_like_ocr_noise(line.text)
        and not _looks_like_prose(line.text)
        and not _looks_like_warning_body_text(line.text)
    ]
    if not eligible:
        return CandidateSet(status="Not found")
    horizontal = [line for line in eligible if _is_horizontal_text(line)]
    if horizontal:
        eligible = horizontal
    class_lines = [line for line in lines if _STRONG_CLASS.search(line.text)]
    associated = [line for line in eligible if _near_class_designation(line, class_lines)]
    if associated:
        adjacent = [
            line
            for line in eligible
            if any(_adjacent_brand_line(line, anchor) for anchor in associated)
        ]
        associated_height = max(_line_height(line) for line in associated)
        prominent = [
            line
            for line in eligible
            if _line_height(line) >= associated_height * 1.5
            and (line.confidence or 0) >= 0.70
        ]
        eligible = [
            *associated,
            *(line for line in adjacent if line not in associated),
            *(
                line
                for line in prominent
                if line not in associated and line not in adjacent
            ),
        ]
    groups = [_brand_group(line, eligible) for line in eligible]
    groups = [
        items
        for items in groups
        if not _looks_like_prose(" ".join(item.text for item in items))
        and not _NON_BRAND_CONTEXT.search(" ".join(item.text for item in items))
    ]
    if not groups:
        return CandidateSet(status="Not found")
    group = min(
        groups,
        key=lambda items: (
            -sum(len(re.findall(r"[A-Za-z]", item.text)) for item in items),
            -_line_height(items[0]),
            -len(items),
            -(items[0].confidence or 0),
            casefolded(whitespace(" ".join(item.text for item in items))),
            min(point.y for point in items[0].polygon),
            min(point.x for point in items[0].polygon),
        ),
    )
    value = whitespace(" ".join(item.text for item in group))
    return CandidateSet(
        status="Found",
        candidates=[Candidate(value=value, evidence=factory.from_lines("brand", group, value))],
    )


def _looks_like_ocr_noise(value: str) -> bool:
    letters = [character.casefold() for character in value if character.isalpha()]
    return len(letters) >= 12 and len(set(letters)) <= 3


def _looks_like_prose(value: str) -> bool:
    words = re.findall(r"[A-Za-z][A-Za-z'-]*", value)
    lowercase_words = [word for word in words if word[:1].islower()]
    return len(words) >= 3 and len(lowercase_words) / len(words) >= 0.60


def _is_horizontal_text(line: OcrLine) -> bool:
    width = max(point.x for point in line.polygon) - min(point.x for point in line.polygon)
    height = max(point.y for point in line.polygon) - min(point.y for point in line.polygon)
    return width >= max(1, height * 1.15)


def _near_class_designation(line: OcrLine, class_lines: list[OcrLine]) -> bool:
    line_bottom = max(point.y for point in line.polygon)
    for class_line in class_lines:
        if class_line.panel_id != line.panel_id or not _same_column(line, class_line):
            continue
        gap = min(point.y for point in class_line.polygon) - line_bottom
        if 0 <= gap <= max(_line_height(line), _line_height(class_line)) * 3:
            return True
    return False


def _adjacent_brand_line(line: OcrLine, anchor: OcrLine) -> bool:
    if line.panel_id != anchor.panel_id or not _same_column(line, anchor):
        return False
    line_top = min(point.y for point in line.polygon)
    line_bottom = max(point.y for point in line.polygon)
    anchor_top = min(point.y for point in anchor.polygon)
    anchor_bottom = max(point.y for point in anchor.polygon)
    gap = max(0, max(line_top, anchor_top) - min(line_bottom, anchor_bottom))
    return gap <= max(_line_height(line), _line_height(anchor)) * 1.5


def _same_normalized_line(first: str, second: str) -> bool:
    return re.sub(r"[^a-z0-9]", "", first.casefold()) == re.sub(
        r"[^a-z0-9]", "", second.casefold()
    )


def _warning_interruption_orders(lines: list[OcrLine]) -> set[int]:
    for index, line in enumerate(lines):
        if not _WARNING.search(line.text):
            continue
        body_lines = _warning_body_lines(lines, index, line)
        part_two = next(
            (
                body_index
                for body_index, candidate in enumerate(body_lines)
                if re.search(r"\(2\)", candidate.text)
            ),
            None,
        )
        if part_two is None:
            return set()
        return {
            candidate.reading_order
            for candidate in body_lines[:part_two]
            if _looks_like_interruption(candidate.text)
        }
    return set()


def _warning_body_orders(lines: list[OcrLine]) -> set[int]:
    for index, line in enumerate(lines):
        if _WARNING.search(line.text):
            return {
                candidate.reading_order
                for candidate in _warning_body_lines(lines, index, line)
            }
    return set()


def _warning_body_lines(
    lines: list[OcrLine], heading_index: int, heading: OcrLine
) -> list[OcrLine]:
    heading_bottom = max(point.y for point in heading.polygon)
    heading_height = max(1, _line_height(heading))
    spatial = sorted(
        (
            candidate
            for candidate in lines
            if candidate.reading_order != lines[heading_index].reading_order
            and candidate.panel_id == heading.panel_id
            and min(point.y for point in candidate.polygon)
            >= heading_bottom - heading_height * 0.25
            and _same_column(heading, candidate)
        ),
        key=lambda item: (
            min(point.y for point in item.polygon),
            min(point.x for point in item.polygon),
            item.reading_order,
        ),
    )
    body: list[OcrLine] = []
    previous_bottom = heading_bottom
    for candidate in spatial:
        candidate_top = min(point.y for point in candidate.polygon)
        candidate_height = max(1, _line_height(candidate))
        if body and candidate_top - previous_bottom > max(heading_height * 4, candidate_height * 4):
            break
        if (
            _PRODUCER.search(candidate.text)
            or _COUNTRY.search(candidate.text)
            or _SCALE.search(candidate.text)
        ):
            break
        body.append(candidate)
        previous_bottom = max(point.y for point in candidate.polygon)
        if re.search(r"health\s+problems\s*[.!]?\s*$", candidate.text, re.I):
            break
    return body


def _same_column(first: OcrLine, second: OcrLine) -> bool:
    first_left = min(point.x for point in first.polygon)
    first_right = max(point.x for point in first.polygon)
    second_left = min(point.x for point in second.polygon)
    second_right = max(point.x for point in second.polygon)
    overlap = max(0, min(first_right, second_right) - max(first_left, second_left))
    smaller_width = max(1, min(first_right - first_left, second_right - second_left))
    if overlap / smaller_width >= 0.25:
        return True
    horizontal_tolerance = max(20, _line_height(first) * 2)
    return abs(first_left - second_left) <= horizontal_tolerance


def _brand_group(first: OcrLine, eligible: list[OcrLine]) -> list[OcrLine]:
    same_row = [
        line
        for line in eligible
        if line is not first
        and line.panel_id == first.panel_id
        and _same_text_row(first, line)
        and len(re.findall(r"[A-Za-z]", line.text)) >= 4
        and casefolded(whitespace(line.text)) != casefolded(whitespace(first.text))
    ]
    if same_row:
        return sorted([first, *same_row], key=lambda item: min(point.x for point in item.polygon))
    group = [first]
    first_bottom = max(point.y for point in first.polygon)
    adjacent = [
        line
        for line in eligible
        if line is not first
        and line.panel_id == first.panel_id
        and _same_column(first, line)
        and _line_height(line) >= max(10, round(_line_height(first) * 0.55))
        and len(re.findall(r"[A-Za-z]", line.text)) >= 4
        and 0
        <= min(point.y for point in line.polygon) - first_bottom
        <= max(12, _line_height(first))
    ]
    if adjacent:
        group.append(
            min(
                adjacent,
                key=lambda line: (
                    min(point.y for point in line.polygon) - first_bottom,
                    min(point.x for point in line.polygon),
                    casefolded(whitespace(line.text)),
                ),
            )
        )
    return group


def _same_text_row(first: OcrLine, second: OcrLine) -> bool:
    first_left = min(point.x for point in first.polygon)
    first_right = max(point.x for point in first.polygon)
    second_left = min(point.x for point in second.polygon)
    second_right = max(point.x for point in second.polygon)
    first_top = min(point.y for point in first.polygon)
    first_bottom = max(point.y for point in first.polygon)
    second_top = min(point.y for point in second.polygon)
    second_bottom = max(point.y for point in second.polygon)
    vertical_overlap = max(0, min(first_bottom, second_bottom) - max(first_top, second_top))
    smaller_height = max(1, min(first_bottom - first_top, second_bottom - second_top))
    horizontal_gap = max(0, max(first_left, second_left) - min(first_right, second_right))
    horizontal_overlap = max(0, min(first_right, second_right) - max(first_left, second_left))
    smaller_width = max(1, min(first_right - first_left, second_right - second_left))
    if horizontal_overlap / smaller_width > 0.35:
        return False
    height = max(first_bottom - first_top, second_bottom - second_top, 1)
    return vertical_overlap / smaller_height >= 0.35 and horizontal_gap <= height * 1.5


_US_STATE_NAMES = re.compile(
    r"\b(?:alabama|alaska|arizona|arkansas|california|colorado|connecticut|delaware|"
    r"florida|georgia|hawaii|idaho|illinois|indiana|iowa|kansas|kentucky|louisiana|"
    r"maine|maryland|massachusetts|michigan|minnesota|mississippi|missouri|montana|"
    r"nebraska|nevada|new\s+hampshire|new\s+jersey|new\s+mexico|new\s+york|"
    r"north\s+carolina|north\s+dakota|ohio|oklahoma|oregon|pennsylvania|"
    r"rhode\s+island|south\s+carolina|south\s+dakota|tennessee|texas|utah|"
    r"vermont|virginia|washington|west\s+virginia|wisconsin|wyoming)\b",
    re.I,
)
_US_STATE_CODE = re.compile(
    r"(?:,|\.)\s*(?:AL|AK|AZ|AR|CA|CO|CT|DE|FL|GA|HI|ID|IL|IN|IA|KS|KY|LA|ME|MD|MA|"
    r"MI|MN|MS|MO|MT|NE|NV|NH|NJ|NM|NY|NC|ND|OH|OK|OR|PA|RI|SC|SD|TN|TX|UT|"
    r"VT|VA|WA|WV|WI|WY)\b",
    re.I,
)
_LONG_STATE_NAMES = (
    "alabama",
    "arizona",
    "arkansas",
    "california",
    "colorado",
    "connecticut",
    "delaware",
    "florida",
    "georgia",
    "hawaii",
    "illinois",
    "indiana",
    "kentucky",
    "louisiana",
    "maryland",
    "michigan",
    "minnesota",
    "mississippi",
    "missouri",
    "montana",
    "nebraska",
    "oklahoma",
    "pennsylvania",
    "tennessee",
    "vermont",
    "virginia",
    "washington",
    "wisconsin",
    "wyoming",
)


def _looks_like_domestic_location(value: str) -> bool:
    if bool(
        re.search(r"\b(?:u\.?s\.?a\.?|united\s+states)\b", value, re.I)
        or _US_STATE_NAMES.search(value)
        or _US_STATE_CODE.search(value)
    ):
        return True
    tokens = re.findall(r"[a-z]{6,}", value.casefold())
    return any(
        SequenceMatcher(None, token, state).ratio() >= 0.70
        for token in tokens
        for state in _LONG_STATE_NAMES
    )


def _industry_location_is_connected(line: OcrLine, following: list[OcrLine]) -> bool:
    """Require an address to be part of the organization block, not elsewhere below it."""

    if _looks_like_domestic_location(line.text):
        return True
    for candidate in following:
        if candidate.panel_id != line.panel_id or not _same_column(line, candidate):
            continue
        if (
            _REGISTRATION_CONTEXT.search(candidate.text)
            or _NON_BRAND_CONTEXT.search(candidate.text)
            or _looks_like_warning_body_text(candidate.text)
            or _line_has_abv(candidate.text)
            or any(pattern.search(candidate.text) for pattern in (_WARNING, _PROOF, _NET, _CLASS))
        ):
            return False
        if _looks_like_domestic_location(candidate.text):
            return True
    return False


def _producer_is_structured(value: str) -> bool:
    normalized = whitespace(value)
    if (
        _looks_like_domestic_location(normalized)
        or _PRODUCER_ENTITY.search(normalized)
        or _INDUSTRY_ORGANIZATION.search(normalized)
    ):
        return True
    remainder = whitespace(_PRODUCER_ROLE.sub("", normalized)).strip(" .,:;-&")
    return len(re.findall(r"[A-Za-z]", remainder)) >= 3


def _drop_contained_candidates(items: list[Candidate]) -> list[Candidate]:
    normalized = [(item, casefolded(whitespace(item.value))) for item in items]
    return [
        item
        for item, value in normalized
        if not any(
            value != other_value and value in other_value
            for _, other_value in normalized
        )
    ]


def _line_height(line: OcrLine) -> int:
    return max(point.y for point in line.polygon) - min(point.y for point in line.polygon)


def _warning_observation(
    lines: list[OcrLine],
    panels: list[PanelResult],
    factory: _EvidenceFactory,
    *,
    source_unreadable: bool,
) -> WarningObservation:
    for index, line in enumerate(lines):
        heading_match = _WARNING.search(line.text)
        if not heading_match:
            continue
        heading, remainder = _warning_heading_and_remainder(line.text, heading_match)
        body_lines: list[OcrLine] = []
        if remainder:
            body_lines.append(line.model_copy(update={"text": remainder}))
        body_lines.extend(_warning_body_lines(lines, index, line))
        content_lines = [
            candidate for candidate in body_lines if not _looks_like_interruption(candidate.text)
        ]
        body_bold = _body_bold_state(content_lines)
        punctuation_normalized = _has_wrap_punctuation_uncertainty(content_lines)
        body = _join_wrapped_lines(content_lines) or None
        heading_evidence = factory.from_line("warning_heading", line)
        body_evidence = (
            factory.from_lines("warning_body", content_lines, body or "") if content_lines else None
        )
        panel = next((item for item in panels if item.panel_id == line.panel_id), None)
        sufficient = bool(panel and panel.coverage_state == "Sufficient")
        previous = next(
            (
                candidate
                for candidate in reversed(lines[:index])
                if candidate.panel_id == line.panel_id and _same_column(candidate, line)
            ),
            None,
        )
        separated = _vertical_separation(previous, line)
        part_two = next(
            (
                body_index
                for body_index, item in enumerate(body_lines)
                if re.search(r"\(2\)", item.text)
            ),
            None,
        )
        continuity = None
        if part_two is not None:
            interruption = any(_looks_like_interruption(item.text) for item in body_lines)
            continuity = not interruption
        contrast = _warning_contrast(line, body_lines) if sufficient else None
        return WarningObservation(
            heading=heading,
            body=body,
            full_text=whitespace(f"{heading} {body or ''}"),
            punctuation_normalized=punctuation_normalized,
            heading_evidence=heading_evidence,
            body_evidence=body_evidence,
            heading_bold=_heading_bold_state(line, previous, content_lines),
            body_bold=body_bold,
            separated=separated,
            continuous=continuity,
            contrast_sufficient=contrast,
            legible=_warning_legibility(line, body_lines, contrast) if sufficient else None,
            physical_size_mm=None,
            reliable_scale=False,
            scale_evidence=None,
            source_unreadable=source_unreadable,
        )
    return WarningObservation(source_unreadable=source_unreadable)


def _warning_heading_and_remainder(value: str, match: re.Match[str]) -> tuple[str, str]:
    heading_value = value[match.start() : match.end()]
    remainder = value[match.end() :]
    trailing_punctuation = re.match(r"[.,;]+", remainder)
    if trailing_punctuation is not None:
        heading_value += trailing_punctuation.group(0)
        remainder = remainder[trailing_punctuation.end() :]
    return _normalize_warning_heading(heading_value), remainder.strip()


def _normalize_warning_heading(value: str) -> str:
    match = re.fullmatch(r"(government)\s+(warning)(\s*:)?", value, re.I)
    if match is None:
        return value
    first, second, colon = match.groups()
    return f"{first} {second}{':' if colon else ''}"


def _join_wrapped_lines(lines: list[OcrLine]) -> str:
    values = [whitespace(item.text) for item in lines if whitespace(item.text)]
    for index in range(len(values) - 1):
        if values[index].endswith(".") and values[index + 1][:1].islower():
            values[index] = values[index][:-1]
    return whitespace(" ".join(values))


def _has_wrap_punctuation_uncertainty(lines: list[OcrLine]) -> bool:
    values = [whitespace(item.text) for item in lines if whitespace(item.text)]
    return any(
        values[index].endswith(".") and values[index + 1][:1].islower()
        for index in range(len(values) - 1)
    )


def _bold_state(density: float | None) -> bool | None:
    if density is None:
        return None
    if density >= _WARNING_THRESHOLDS["headingBoldInkDensityPassGte"]:
        return True
    if density <= _WARNING_THRESHOLDS["headingBoldInkDensityFailLte"]:
        return False
    return None


def _body_bold_state(lines: list[OcrLine]) -> bool | None:
    content = [item for item in lines if not _looks_like_interruption(item.text)]
    if not content or any(item.ink_density is None for item in content):
        return None
    densities = [item.ink_density for item in content if item.ink_density is not None]
    average = sum(densities) / len(densities)
    if average >= _WARNING_THRESHOLDS["bodyBoldMeanInkDensityPassGte"]:
        return True
    if average <= _WARNING_THRESHOLDS["bodyNotBoldMeanInkDensityPassLte"]:
        return False
    return None


def _heading_bold_state(
    heading: OcrLine, previous: OcrLine | None, body_lines: list[OcrLine]
) -> bool | None:
    if heading.ink_density is None:
        return None
    density_state = _bold_state(heading.ink_density)
    if density_state is True:
        return True
    heading_height = _line_height(heading)
    previous_height = 0
    if previous is not None and _nearby_preceding_line(previous, heading):
        previous_height = _line_height(previous)
    height_state: bool | None = None
    if previous_height > 0:
        height_ratio = heading_height / previous_height
        if height_ratio >= 1.18:
            height_state = True
        if height_ratio <= 1.08:
            height_state = False
    if not body_lines or any(line.ink_density is None for line in body_lines):
        return None
    body_densities = [line.ink_density for line in body_lines if line.ink_density is not None]
    body_average = sum(body_densities) / len(body_densities)
    if body_average <= 0:
        return None
    ratio = heading.ink_density / body_average
    if ratio >= _WARNING_THRESHOLDS["headingToBodyDensityPassGte"]:
        return True
    if ratio <= _WARNING_THRESHOLDS["headingToBodyDensityFailLte"] and height_state is False:
        return False
    return height_state if height_state is True else None


def _vertical_separation(previous: OcrLine | None, heading: OcrLine) -> bool | None:
    if previous is None:
        return None
    gap = min(point.y for point in heading.polygon) - max(point.y for point in previous.polygon)
    heading_height = _line_height(heading)
    previous_height = _line_height(previous)
    if heading_height <= 0 or previous_height <= 0:
        return None
    comparison_height = min(heading_height, previous_height)
    if gap > comparison_height * 3:
        return None
    if gap >= comparison_height * _WARNING_THRESHOLDS[
        "separationGapPassLineHeightRatioGte"
    ]:
        if _unexpected_surrounding_text(previous.text) and gap < comparison_height * 2:
            return None
        return True
    if _unexpected_surrounding_text(previous.text):
        return None
    if gap <= comparison_height * _WARNING_THRESHOLDS[
        "separationGapFailLineHeightRatioLte"
    ]:
        return False
    return None


def _warning_contrast(heading: OcrLine, body_lines: list[OcrLine]) -> bool | None:
    content = [item for item in [heading, *body_lines] if not _looks_like_interruption(item.text)]
    if not content or any(
        item.ink_density is None or item.local_contrast is None for item in content
    ):
        return None
    contrasts = [item.local_contrast for item in content if item.local_contrast is not None]
    if min(contrasts) < _WARNING_THRESHOLDS["contrastFailLt"]:
        return False
    confidences = [item.confidence for item in content if item.confidence is not None]
    if (
        len(confidences) != len(content)
        or min(confidences) < _WARNING_THRESHOLDS["ocrSignalPassGte"]
    ):
        return None
    return True


def _nearby_preceding_line(previous: OcrLine | None, heading: OcrLine) -> bool:
    if previous is None:
        return False
    gap = min(point.y for point in heading.polygon) - max(point.y for point in previous.polygon)
    comparison_height = max(_line_height(heading), _line_height(previous), 1)
    return 0 <= gap <= comparison_height * 3


def _warning_legibility(
    heading: OcrLine, body_lines: list[OcrLine], contrast: bool | None
) -> bool | None:
    if contrast is not True:
        return None
    confidences = [
        item.confidence
        for item in [heading, *body_lines]
        if item.confidence is not None and not _looks_like_interruption(item.text)
    ]
    if not confidences:
        return None
    if min(confidences) >= _WARNING_THRESHOLDS["ocrSignalPassGte"]:
        return True
    if min(confidences) < _WARNING_THRESHOLDS["ocrSignalFailLt"]:
        return False
    return None


def _unexpected_surrounding_text(value: str) -> bool:
    text = whitespace(value)
    return bool(
        _looks_like_interruption(text) and not _PRODUCER.search(text) and not re.search(r"\d", text)
    )


def _looks_like_interruption(value: str) -> bool:
    text = whitespace(value)
    if (
        text.startswith(("(1)", "(2)"))
        or _WARNING_BODY_TERM.search(text)
        or _contains_warning_like_word(text)
    ):
        return False
    return bool(text and any(character.isalpha() for character in text) and text.upper() == text)


def _looks_like_warning_body_text(value: str) -> bool:
    text = whitespace(value)
    if text.startswith(("(1)", "(2)")):
        return True
    tokens = set(re.findall(r"[A-Za-z]+", text.casefold()))
    return len(tokens & _WARNING_BODY_WORDS) >= 3


def _contains_warning_like_word(value: str) -> bool:
    tokens = re.findall(r"[A-Za-z]{4,}", value.casefold())
    return any(
        SequenceMatcher(None, token, expected, autojunk=False).ratio() >= 0.72
        for token in tokens
        for expected in _WARNING_BODY_WORDS
    )
