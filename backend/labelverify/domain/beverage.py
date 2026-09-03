from __future__ import annotations

import re

from labelverify.contracts.models import BeverageType
from labelverify.domain.types import ObservedCandidates

_VOCABULARIES: dict[BeverageType, tuple[str, ...]] = {
    "distilled_spirits": (
        "bourbon",
        "whiskey",
        "whisky",
        "vodka",
        "gin",
        "rum",
        "tequila",
        "brandy",
        "cognac",
        "liqueur",
        "cordial",
        "neutral spirits",
        "grain spirits",
        "distilled spirits",
    ),
    "wine": (
        "wine",
        "merlot",
        "cabernet",
        "chardonnay",
        "pinot",
        "riesling",
        "rose",
        "rosé",
        "sauvignon",
        "zinfandel",
        "syrah",
        "shiraz",
        "muscat",
        "sangiovese",
        "malbec",
        "tempranillo",
        "grenache",
        "prosecco",
        "sangria",
        "vermouth",
        "champagne",
    ),
    "malt_beverage": (
        "malt beverage",
        "beer",
        "ale",
        "lager",
        "stout",
        "porter",
        "pilsner",
        "ipa",
        "india pale ale",
    ),
}


def infer_beverage_type(
    observed: ObservedCandidates,
) -> tuple[BeverageType | None, float | None, str, bool]:
    scores = beverage_type_scores(observed)
    matched = [name for name, score in scores.items() if score > 0]
    if len(matched) != 1:
        return (
            None,
            None,
            "The label did not provide one unambiguous beverage-type signal",
            len(matched) > 1,
        )
    winner = matched[0]
    score = scores[winner]
    confidence = min(0.98, 0.76 + 0.06 * score)
    return (
        winner,
        confidence,
        f"Readable class or type terms support {winner}",
        False,
    )


def beverage_type_hits(observed: ObservedCandidates) -> set[BeverageType]:
    return {name for name, score in beverage_type_scores(observed).items() if score > 0}


def beverage_type_scores(observed: ObservedCandidates) -> dict[BeverageType, int]:
    sources = ((observed.field("class_type"), 2),)
    scores: dict[BeverageType, int] = {name: 0 for name in _VOCABULARIES}
    for candidates, weight in sources:
        values = [_semantic_text(candidate.value) for candidate in candidates.candidates]
        for name, terms in _VOCABULARIES.items():
            scores[name] += weight * sum(
                any(_contains_term(value, term) for value in values) for term in terms
            )
    return scores


def _semantic_text(value: str) -> str:
    expanded = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", value)
    expanded = re.sub(r"(?<=[A-Za-z])(?=\d)|(?<=\d)(?=[A-Za-z])", " ", expanded)
    normalized = " ".join(
        re.sub(r"[^\w%é]+", " ", expanded, flags=re.UNICODE).casefold().split()
    )
    # OCR commonly removes a space before short connective words. Repair only
    # beverage vocabulary boundaries, preserving the original evidence text.
    return re.sub(
        r"\b(wine|beer|ale|lager|vodka|whisk(?:e)?y|rum|gin)(with|from|by)\b",
        r"\1 \2",
        normalized,
    )


def _contains_term(value: str, term: str) -> bool:
    return bool(re.search(rf"(?<!\w){re.escape(term)}(?!\w)", value, re.I))
