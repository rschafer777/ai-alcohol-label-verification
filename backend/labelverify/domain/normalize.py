from __future__ import annotations

import re
import unicodedata
from decimal import Decimal, InvalidOperation

_SPACE = re.compile(r"\s+")
_PUNCT = re.compile(r"[^\w\s]", re.UNICODE)
_ABV = re.compile(r"(?<!\d)(\d{1,3}(?:\.\d+)?)\s*%(?:\s*(?:alc(?:ohol)?\.?\s*/?\s*vol\.?))?", re.I)
_PROOF = re.compile(r"(?<!\d)(\d{1,3}(?:\.\d+)?)\s*proof\b", re.I)
_VOLUME = re.compile(
    r"(?<!\d)(\d+(?:\.\d+)?)\s*"
    r"(fl\.?\s*(?:oz|0z)\.?|fluid\s+ounces?|pints?|pts?\.?|quarts?|qts?\.?|"
    r"gallons?|gals?\.?|ml|m[lL]|lit(?:er|re)s?|[lL])\b",
    re.I,
)


def whitespace(value: str) -> str:
    return _SPACE.sub(" ", unicodedata.normalize("NFKC", value)).strip()


def casefolded(value: str) -> str:
    return whitespace(value).casefold()


def punctuation_folded(value: str) -> str:
    return whitespace(_PUNCT.sub("", casefolded(value)))


def parse_decimal(value: str) -> Decimal | None:
    try:
        return Decimal(value.replace(",", "").strip())
    except InvalidOperation:
        return None


def parse_abv(value: str) -> Decimal | None:
    match = _ABV.search(value)
    return parse_decimal(match.group(1)) if match else None


def parse_proof(value: str) -> Decimal | None:
    match = _PROOF.search(value)
    return parse_decimal(match.group(1)) if match else None


def parse_volume_ml(value: str) -> Decimal | None:
    match = _VOLUME.search(value)
    if not match:
        return None
    quantity = parse_decimal(match.group(1))
    if quantity is None:
        return None
    unit = match.group(2).casefold()
    compact = re.sub(r"[.\s]", "", unit)
    if compact.startswith("fl"):
        compact = compact.replace("0", "o")
    multipliers = {
        "l": Decimal("1000"),
        "liter": Decimal("1000"),
        "litre": Decimal("1000"),
        "liters": Decimal("1000"),
        "litres": Decimal("1000"),
        "floz": Decimal("29.5735295625"),
        "fluidounce": Decimal("29.5735295625"),
        "fluidounces": Decimal("29.5735295625"),
        "pint": Decimal("473.176473"),
        "pints": Decimal("473.176473"),
        "pt": Decimal("473.176473"),
        "pts": Decimal("473.176473"),
        "quart": Decimal("946.352946"),
        "quarts": Decimal("946.352946"),
        "qt": Decimal("946.352946"),
        "qts": Decimal("946.352946"),
        "gallon": Decimal("3785.411784"),
        "gallons": Decimal("3785.411784"),
        "gal": Decimal("3785.411784"),
        "gals": Decimal("3785.411784"),
    }
    return quantity * multipliers.get(compact, Decimal("1"))


def reference_volume_ml(value: Decimal, unit: str) -> Decimal:
    multipliers = {
        "mL": Decimal("1"),
        "L": Decimal("1000"),
        "fl oz": Decimal("29.5735295625"),
        "pt": Decimal("473.176473"),
        "qt": Decimal("946.352946"),
        "gal": Decimal("3785.411784"),
    }
    return value * multipliers[unit]


def warning_text(value: str) -> str:
    normalized = whitespace(value)
    normalized = re.sub(r"(?<=\S)(\([12]\))", r" \1", normalized)
    return re.sub(r"(\([12]\))(?=\S)", r"\1 ", normalized)
