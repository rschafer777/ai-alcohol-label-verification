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
        "chianti",
        "barolo",
        "brunello",
        "valpolicella",
        "amarone",
        "rioja",
        "cava",
        "bordeaux",
        "burgundy",
        "chablis",
        "sancerre",
        "beaujolais",
        "moscato",
        "nebbiolo",
        "montepulciano",
        "primitivo",
        "vermentino",
        "lambrusco",
        "gewurztraminer",
        "viognier",
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
        "bock",
        "doppelbock",
        "hefeweizen",
        "weissbier",
        "witbier",
        "kolsch",
        "saison",
        "dunkel",
        "marzen",
        "oktoberfest",
        "tripel",
        "dubbel",
        "gose",
        "radler",
        "malt liquor",
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


_HINT_CONFIDENCE = 0.6
_HINTS: dict[BeverageType, re.Pattern[str]] = {
    "distilled_spirits": re.compile(r"\b(?:distilled|distillery|distillers?|proof)\b", re.I),
    "malt_beverage": re.compile(r"\b(?:brewed|brewery|brewing|brewers?)\b", re.I),
    "wine": re.compile(r"\b(?:winery|vineyards?|vinted|cellars?|sulfites?|vintners?)\b", re.I),
}


def infer_beverage_type(
    observed: ObservedCandidates,
) -> tuple[BeverageType | None, float | None, str, bool]:
    scores = beverage_type_scores(observed)
    matched = [name for name, score in scores.items() if score > 0]
    if len(matched) > 1:
        return (
            None,
            None,
            "The label did not provide one unambiguous beverage-type signal",
            True,
        )
    if not matched:
        hinted = _hinted_families(observed)
        if len(hinted) == 1:
            # No class designation was read. Production statements ("distilled and bottled
            # by", "brewed by", "winery") and a proof statement still point to one family;
            # the low confidence asks the reviewer to confirm before relying on it.
            return (
                hinted[0],
                _HINT_CONFIDENCE,
                f"No class or type was read; production statements suggest {hinted[0]}",
                False,
            )
        return (
            None,
            None,
            "The label did not provide one unambiguous beverage-type signal",
            False,
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


def _hinted_families(observed: ObservedCandidates) -> list[BeverageType]:
    texts = [candidate.value for candidate in observed.field("producer").candidates]
    texts.extend(candidate.value for candidate in observed.field("wine_sulfites").candidates)
    if observed.field("proof").status in {"Found", "Ambiguous"}:
        texts.append("proof")
    joined = " ".join(texts)
    return [name for name, pattern in _HINTS.items() if pattern.search(joined)]


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
    normalized = " ".join(re.sub(r"[^\w%é]+", " ", expanded, flags=re.UNICODE).casefold().split())
    # OCR commonly removes a space before short connective words. Repair only
    # beverage vocabulary boundaries, preserving the original evidence text.
    return re.sub(
        r"\b(wine|beer|ale|lager|vodka|whisk(?:e)?y|rum|gin)(with|from|by)\b",
        r"\1 \2",
        normalized,
    )


def _contains_term(value: str, term: str) -> bool:
    return bool(re.search(rf"(?<!\w){re.escape(term)}(?!\w)", value, re.I))
