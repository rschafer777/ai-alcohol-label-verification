from __future__ import annotations

import re
import unicodedata
from decimal import Decimal, InvalidOperation
from difflib import SequenceMatcher

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


_WARNING_MARKER = re.compile(r"[(\[]?\s*([12])\s*[)\].:]?(?=\s*[A-Za-z(]|$)")
_GLUED_MARKER = re.compile(r"(?<![\w.])([12])(?=[A-Za-z])")


def warning_words(value: str) -> str:
    """The warning as a comparable word sequence.

    OCR renders the statutory markers as "(1)", "1)", "1." or glued "1According", and it
    drops or invents spacing around commas and periods. Words are what the statute fixes, so
    both markers become bare digits and every punctuation mark becomes a word boundary.
    """

    text = casefolded(value)
    text = _GLUED_MARKER.sub(r"\1 ", text)
    text = _WARNING_MARKER.sub(r" \1 ", text)
    return whitespace(_PUNCT.sub(" ", text))


_PRODUCER_STATEMENT = re.compile(
    r"\b(?:bottled|distilled|produced|manufactured|blended|imported|packed|brewed|canned|"
    r"filled|vinted|cellared)\s*(?:(?:and|&)\s*(?:bottled|canned|packed|filled)\s+)?by\b",
    re.I,
)


def looks_like_producer_statement(value: str) -> bool:
    """True for a name-and-address statement ("bottled by ..."), whatever else it carries."""

    return _PRODUCER_STATEMENT.search(value) is not None


_BUSINESS_ENTITY = re.compile(
    r"\b(?:llc|l\.l\.c\.?|inc\.?|incorporated|corp\.?|corporation|ltd\.?|limited|"
    r"company|co\.|gmbh|s\.a\.|s\.r\.l\.|pty)\b|\b\d{5}(?:-\d{4})?\b",
    re.I,
)


def looks_like_business_line(value: str) -> bool:
    """True for a company name with an entity suffix, an address line, or a role statement.

    Such a line names the responsible business ("OLD TOM DISTILLERY LLC, FRANKFORT, KY"),
    not the brand under which the product is sold.
    """

    return (
        looks_like_producer_statement(value)
        or _BUSINESS_ENTITY.search(value) is not None
        or US_STATE_CODE.search(value) is not None
    )


_US_DESIGNATION = re.compile(
    r"^(?:u\.?\s*s\.?\s*a?\.?|united\s+states(?:\s+of\s+america)?|america|the\s+usa)$",
    re.I,
)


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
US_STATE_CODE = re.compile(
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


def looks_like_domestic_location(value: str) -> bool:
    """True for a United States address, tolerating OCR damage in long state names."""

    if bool(
        re.search(r"\b(?:u\.?s\.?a\.?|united\s+states)\b", value, re.I)
        or _US_STATE_NAMES.search(value)
        or US_STATE_CODE.search(value)
    ):
        return True
    tokens = re.findall(r"[a-z]{6,}", value.casefold())
    return any(
        SequenceMatcher(None, token, state).ratio() >= 0.70
        for token in tokens
        for state in _LONG_STATE_NAMES
    )


def is_domestic_origin(value: str) -> bool:
    """True when a country-of-origin reading names the United States."""

    return value.strip().casefold() == "united states" or bool(
        _US_DESIGNATION.fullmatch(value.strip())
    )
