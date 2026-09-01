from __future__ import annotations

import re
import unicodedata
from decimal import Decimal, InvalidOperation

_SPACE = re.compile(r"\s+")
_PUNCT = re.compile(r"[^\w\s]", re.UNICODE)
_ABV = re.compile(r"(?<!\d)(\d{1,3}(?:\.\d+)?)\s*%(?:\s*(?:alc(?:ohol)?\.?\s*/?\s*vol\.?))?", re.I)
_PROOF = re.compile(r"(?<!\d)(\d{1,3}(?:\.\d+)?)\s*proof\b", re.I)
_VOLUME = re.compile(r"(?<!\d)(\d+(?:\.\d+)?)\s*(ml|m[lL]|lit(?:er|re)s?|[lL])\b", re.I)


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
    return (
        quantity * Decimal(1000)
        if unit in {"l", "liter", "litre", "liters", "litres"}
        else quantity
    )


def reference_volume_ml(value: Decimal, unit: str) -> Decimal:
    return value * Decimal(1000) if unit == "L" else value


def warning_text(value: str) -> str:
    normalized = whitespace(value)
    normalized = re.sub(r"(?<=\S)(\([12]\))", r" \1", normalized)
    return re.sub(r"(\([12]\))(?=\S)", r"\1 ", normalized)
