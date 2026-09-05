from __future__ import annotations

import re
from collections.abc import Callable, Iterable
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
from labelverify.domain.normalize import (
    US_STATE_CODE,
    casefolded,
    is_domestic_origin,
    looks_like_domestic_location,
    parse_volume_ml,
    warning_words,
    whitespace,
)
from labelverify.domain.types import ObservedCandidates, WarningObservation

_PERCENT = re.compile(r"\b\d{1,3}(?:\.\d+)?\s*%", re.I)
# "vol" arrives OCR-damaged as "vo", "ol", "vl", or "voi" on small type; after an "alc"
# prefix those forms still name the alcohol-by-volume statement.
_ABV_CONTEXT = re.compile(
    r"\b(?:alc(?:ohol)?\.?\s*(?:/|by)?\s*(?:vol|vo|ol|vl|voi)\.?|abv)\b",
    re.I,
)
_ALC_PREFIX = re.compile(r"\balc(?:ohol)?\.?\s*$", re.I)
_BY_VOL_SUFFIX = re.compile(r"^\s*(?:by\s*|/\s*)vol\.?\b", re.I)
_ALC_VOLUME_LOOSE = re.compile(r"\balc[a-z0-9]{0,10}.*\bvol(?:ume)?\b", re.I)
_PROOF = re.compile(r"\b\d{1,3}(?:\.\d+)?\s*proof\b", re.I)
_ZERO_FOR_O_OUNCE = re.compile(r"\b0z\b", re.I)
_NET = re.compile(
    r"\b\d+(?:\.\d+)?\s*(?:fl\.?\s*(?:oz|0z)\.?|fluid\s+ounces?|pints?|pts?\.?|"
    r"quarts?|qts?\.?|gallons?|gals?\.?|ml|mL|L|liters?|litres?)\b",
    re.I,
)
# Wine designations of geographic significance and varietal names that stand as the
# class or type statement on wine labels.
_WINE_DESIGNATIONS = (
    r"chianti(?:\s+classico)?|barolo|barbaresco|brunello|valpolicella|amarone|soave|lambrusco|"
    r"nebbiolo|montepulciano|primitivo|vermentino|verdicchio|moscato|rioja|cava|bordeaux|"
    r"bourgogne|burgundy|chablis|sancerre|beaujolais|madeira|gew[uü]rztraminer|"
    r"gr[uü]ner\s+veltliner|albari[nñ]o|carm[eé]n[eè]re|pinotage|chenin\s+blanc|s[eé]millon|"
    r"petite\s+sirah|petit\s+verdot|meritage|viognier|(?:red|white|ros[eé]|table|dessert|"
    r"sparkling|fortified)\s+wine"
)
# A wine designation or varietal that opens a line names the wine ("Chianti Rufina",
# "Moscato d'Asti", "Malbec Mendoza"): the words after it are its region or its style.
_WINE_FIRST = re.compile(
    r"^(?:merlot|cabernet|chardonnay|pinot|riesling|sauvignon|zinfandel|syrah|shiraz|"
    r"muscat|sangiovese|malbec|tempranillo|grenache|prosecco|moscato|"
    + _WINE_DESIGNATIONS
    + r")\b",
    re.I,
)
# Beer styles that appear as the class or type statement on craft labels.
_BEER_STYLES = (
    r"bock|doppelbock|hefeweizen|weissbier|weizen|witbier|k[oö]lsch|saison|dunkel|"
    r"m[aä]rzen|oktoberfest|tripel|dubbel|quadrupel|gose|radler|barleywine|malt\s+liquor"
)
_CLASS = re.compile(
    r"\b(?:bourbon|whisk(?:e)?y|vodka|gin|rum|tequila|brandy|liqueur|cordial|spirits?|"
    r"(?:grape\s*)?wine(?:\s*with)?|merlot|cabernet|chardonnay|pinot|riesling|ros[eé]|sauvignon|zinfandel|"
    r"syrah|shiraz|muscat|sangiovese|malbec|tempranillo|grenache|prosecco|"
    r"sangria|vermouth|port|sherry|champagne|sparkling\s+wine|"
    r"malt\s+beverage|beer|ale|lager|stout|porter|pilsner|ipa|india\s+pale\s+ale|"
    r"near\s+beer|cereal\s+beverage|hard\s+seltzer|"
    + _BEER_STYLES
    + r"|"
    + _WINE_DESIGNATIONS
    + r")\b",
    re.I,
)
_STRONG_CLASS = re.compile(
    r"\b(?:bourbon|whisk(?:e)?y|vodka|gin|rum|tequila|brandy|liqueur|cordial|"
    r"neutral\s+spirits?|grain\s+spirits?|distilled\s+spirits?|"
    r"(?:grape\s*)?wine(?:\s*with)?|merlot|cabernet|chardonnay|pinot|riesling|ros[eé]|sauvignon|zinfandel|"
    r"syrah|shiraz|muscat|sangiovese|malbec|tempranillo|grenache|prosecco|"
    r"sangria|vermouth|port|sherry|champagne|beer|ale|lager|"
    r"stout|porter|pilsner|india\s+pale\s+ale|near\s+beer|hard\s+seltzer|"
    + _BEER_STYLES
    + r"|"
    + _WINE_DESIGNATIONS
    + r")\b",
    re.I,
)
# The second role word after "and" may arrive OCR-damaged ("brewed and bottld by"), so
# any short word is accepted there; "by" anchors the phrase.
_PRODUCER_ROLE = re.compile(
    r"\b(?:bottled|distilled|produced|manufactured|blended|imported|packed|brewed|"
    r"canned|filled|vinted|cellared)\s*(?:(?:and|&)\s*[a-z]{3,12})?[\s.,:]*by\b",
    re.I,
)
_PRODUCER_ENTITY = re.compile(
    # A single trailing letter commonly appears when small legal suffixes touch a border or
    # bottle texture ("LLCE"). The suffix remains a reliable organization anchor while the
    # retained evidence preserves the OCR transcription for human review.
    r"\b(?:llc[a-z]?|l\.l\.c\.|inc\.?|corp\.?|corporation|ltd\.?|company|co\.?|imports?)\b",
    re.I,
)
_PRODUCER = re.compile(f"(?:{_PRODUCER_ROLE.pattern}|{_PRODUCER_ENTITY.pattern})", re.I)
_INDUSTRY_ORGANIZATION = re.compile(r"\b(?:brewery|brewing|winery|distillery)\b", re.I)
# Origin phrases tolerate one OCR-damaged character in "product" and a missing space after
# "de" so a French bilingual statement such as "PRODUIT DEFRANCE" still names the country.
_COUNTRY = re.compile(
    r"\b(?:pro?d[a-z]{0,3}ct\s+of|produce\s+of|produit\s+de|wine\s+of|made\s+in|"
    r"country\s+of\s+origin\s*:?|imported\s+from|hecho\s+en)\s*"
    r"([A-Za-z][A-Za-z .']{1,40})",
    re.I,
)
# An origin phrase names a country only when what follows is one. "Made in small
# batches", "product of our family farm", and "wine of the month club" are copy, not
# origin statements, and a United States location after "wine of" is a domestic origin.
_COUNTRY_ALTERNATION = (
    r"afghanistan|albania|algeria|andorra|angola|antigua\s+and\s+barbuda|argentina|armenia|"
    r"aruba|australia|austria|azerbaijan|bahamas|bahrain|bangladesh|barbados|belarus|belgium|"
    r"belize|benin|bermuda|bhutan|bolivia|bosnia\s+and\s+herzegovina|botswana|brazil|brunei|"
    r"bulgaria|burkina\s+faso|burundi|cabo\s+verde|cape\s+verde|cambodia|cameroon|canada|"
    r"cayman\s+islands|central\s+african\s+republic|chad|chile|china|colombia|comoros|congo|"
    r"costa\s+rica|cote\s+d['’]?ivoire|ivory\s+coast|croatia|cuba|curacao|cyprus|"
    r"czech\s+republic|czechia|denmark|djibouti|dominica|dominican\s+republic|ecuador|egypt|"
    r"el\s+salvador|england|equatorial\s+guinea|eritrea|estonia|eswatini|swaziland|ethiopia|"
    r"fiji|finland|france|french\s+polynesia|gabon|gambia|georgia|germany|ghana|gibraltar|"
    r"great\s+britain|greece|greenland|grenada|guadeloupe|guam|guatemala|guernsey|guinea|"
    r"guinea\s+bissau|guyana|haiti|holland|honduras|hong\s+kong|hungary|iceland|india|"
    r"indonesia|iran|iraq|ireland|isle\s+of\s+man|israel|italy|jamaica|japan|jersey|jordan|"
    r"kazakhstan|kenya|kiribati|korea|south\s+korea|republic\s+of\s+korea|kosovo|kuwait|"
    r"kyrgyzstan|laos|latvia|lebanon|lesotho|liberia|libya|liechtenstein|lithuania|"
    r"luxembourg|macau|macedonia|north\s+macedonia|madagascar|malawi|malaysia|maldives|mali|"
    r"malta|marshall\s+islands|martinique|mauritania|mauritius|mexico|micronesia|moldova|"
    r"monaco|mongolia|montenegro|morocco|mozambique|myanmar|burma|namibia|nauru|nepal|"
    r"netherlands|netherlands\s+antilles|new\s+zealand|nicaragua|niger|nigeria|"
    r"northern\s+ireland|norway|oman|pakistan|palau|panama|papua\s+new\s+guinea|paraguay|"
    r"peru|philippines|poland|portugal|puerto\s+rico|qatar|reunion|romania|russia|"
    r"russian\s+federation|rwanda|saint\s+kitts\s+and\s+nevis|saint\s+lucia|saint\s+vincent|"
    r"samoa|san\s+marino|sao\s+tome\s+and\s+principe|saudi\s+arabia|scotland|senegal|serbia|"
    r"seychelles|sierra\s+leone|singapore|sint\s+maarten|slovakia|slovenia|solomon\s+islands|"
    r"somalia|south\s+africa|south\s+sudan|spain|sri\s+lanka|sudan|suriname|sweden|"
    r"switzerland|syria|tahiti|taiwan|tajikistan|tanzania|thailand|timor\s+leste|"
    r"east\s+timor|togo|tonga|trinidad\s+and\s+tobago|trinidad|tunisia|turkey|turkiye|"
    r"turkmenistan|tuvalu|uganda|ukraine|united\s+arab\s+emirates|uae|united\s+kingdom|uk|"
    r"united\s+states|united\s+states\s+of\s+america|usa|america|uruguay|uzbekistan|vanuatu|"
    r"vatican\s+city|venezuela|vietnam|viet\s+nam|virgin\s+islands|wales|yemen|zambia|"
    r"zimbabwe"
)
_COUNTRY_NAMES = re.compile(
    r"^(?:the\s+)?(?:" + _COUNTRY_ALTERNATION + r")\.?$",
    re.I,
)
_COUNTRY_KNOWN_CONTEXT = re.compile(
    r"\b(?:pro?d[a-z]{0,3}ct\s+of|produce\s+of|produit\s+de|wine\s+of|made\s+in|"
    r"country\s+of\s+origin\s*:?|imported\s+from|hecho\s+en)\s*"
    r"((?:the\s+)?(?:" + _COUNTRY_ALTERNATION + r"))\b",
    re.I,
)
# The heading with its last letter tolerated missing: a photograph of a curved label often
# loses the edge of the line ("GOVERNMENT WARNIN").
_WARNING = re.compile(r"government\s+warnin(?:g)?\s*:?", re.I)
# A heading cut at its start ("...ERNMENT WARNING: (1) ACCORDING TO THE SURGEON"): only
# counted when the statutory opening follows, so a "Proposition 65 warning", a brewer's
# note, or any other cautionary line never passes as the federal statement. Such a line
# anchors a body fragment without a heading.
_WARNING_EDGE = re.compile(
    r"(?:[a-z]{0,10}ment\s+)?warning\s*:?\s*"
    r"(?=[(\[]?\s*1[)\]]?\s*accord\w*(?:\s+to(?:\s+th\w*(?:\s+surg|[\s.,;:|-]*$)|[\s.,;:|-]*$)|"
    r"[\s.,;:|-]*$))",
    re.I,
)
# Appellations of origin under 27 CFR 4.25: the United States, a state, a county, a
# recognized viticultural area, or a foreign country or region named by an origin statement.
_APPELLATION = re.compile(
    r"\b(?:american|alabama|alaska|arizona|arkansas|california|colorado|connecticut|"
    r"delaware|florida|georgia|hawaii|idaho|illinois|indiana|iowa|kansas|kentucky|"
    r"louisiana|maine|maryland|massachusetts|michigan|minnesota|mississippi|missouri|"
    r"montana|nebraska|nevada|new\s+hampshire|new\s+jersey|new\s+mexico|new\s+york|"
    r"north\s+carolina|north\s+dakota|ohio|oklahoma|oregon|pennsylvania|rhode\s+island|"
    r"south\s+carolina|south\s+dakota|tennessee|texas|utah|vermont|virginia|washington|"
    r"west\s+virginia|wisconsin|wyoming|napa\s+valley|sonoma(?:\s+(?:coast|county|valley))?|"
    r"willamette\s+valley|columbia\s+valley|finger\s+lakes|paso\s+robles|"
    r"russian\s+river\s+valley|santa\s+barbara|monterey|mendocino|lodi|walla\s+walla|"
    r"central\s+coast|north\s+coast|sierra\s+foothills|texas\s+hill\s+country|"
    r"long\s+island|[A-Za-z]+\s+county|"
    r"(?:pro?d[a-z]{0,3}ct|wine|produce)\s+of\s+[A-Za-z][A-Za-z .'-]{1,60})\b",
    re.I,
)
_SULFITES = re.compile(r"\bcontains?\s*(?:sulfites?|a\s+sulfiting\s+agent)\b", re.I)
_ADDRESS_SHAPE = re.compile(
    r"\b\d{5}(?:-\d{4})?\b|"
    r"\b(?:street|st\.|avenue|ave\.|road|rd\.|highway|hwy\.?|blvd\.?|boulevard|suite|"
    r"ste\.?|p\.?o\.?\s*box)\b",
    re.I,
)
_WARNING_BODY_TERM = re.compile(
    r"\b(?:according|surgeon|general|women|should|drink|alcoholic|beverages|"
    r"pregnancy|risk|birth|defects|consumption|impairs|ability|drive|car|"
    r"operate|machinery|cause|health|problems)\b",
    re.I,
)
# Every word of the statutory statement, including the short ones.
_STATUTE_SEQUENCE = tuple(warning_words(str(contracts().rules["warning"]["bodyExact"])).split())
# Every two- and three-word run of the statement in its order.
_STATUTE_RUNS = frozenset(
    _STATUTE_SEQUENCE[start : start + size]
    for size in (2, 3)
    for start in range(len(_STATUTE_SEQUENCE) - size + 1)
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
    r"\bm[eé]thode\s+champenoise\b|"
    r"\b(?:notes?|aromas?|hints?|flavou?rs?)\s+of\b|\bon\s+the\s+(?:palate|nose)\b|"
    r"\bbest\s+served\b|\bserved?\s+(?:chilled|cold|neat|warm|over\s+ice)\b|"
    r"\bkeep\s+(?:refrigerated|cold|frozen)\b|\bshake\s+well\b|"
    r"\b(?:long|smooth|lingering)\s+finish\b|"
    r"\bfrom\s+(?:certified\s+)?(?:organic\s+)?(?:sugar\s+cane|grapes?|grain|corn|fruit)\b|"
    r"\b(?:orange|lemon|lime|citrus)\s+peel\b|"
    r"\bhoney\s+and\s+spices?\b|"
    r"\bconta[a-z]{0,5}\s*sulf[a-z]*\b|"
    r"^\s*drink\b|ref\s*\d+\s*[c\u00a2]|\b(?:ca\s*)?crv(?=\d|\b)|"
    r"\bdeposit\b|\brefund\b|\brecycl[a-z]*\b|"
    r"^\s*usda\s*$|^\s*(?:usda\s+)?organic\s*$|"
    r"\b(?:est(?:ablished)?\.?|since|founded|anno)\s*(?:in\s+)?\d{4}\b|^\s*\d{4}\s*$|"
    r"^\s*fl\.?\s*(?:oz|0z)\.?\s*$|"
    r"https?://|www\.|\.(?:com|org|net)\b)",
    re.I,
)
# A color statement ("CARAMEL COLOR ADDED", "ARTIFICIALLY COLORED") is a mandatory
# statement, and a line opening with a long number is a code, a lot, or a barcode read.
_COLOR_STATEMENT = re.compile(
    r"\b(?:caramel\s+colou?r|colou?r(?:ing)?\s+added|artificial(?:ly)?\s+colou?r(?:ed)?|"
    r"certified\s+colou?rs?|with\s+caramel)\b",
    re.I,
)
_CODE_PREFIX = re.compile(r"^\s*\d{5,}\b")
_ORIGIN_COPY = re.compile(
    r"\b(?:born|made|crafted|distilled|brewed|produced|founded)\s+in\s+(?:the\s+)?(.{3,40})",
    re.I,
)


def _origin_copy(value: str) -> bool:
    """ "BORN IN SAN FRANCISCO IN 1992" is origin copy; "BORN IN A BARN" is a name, because
    nothing after "in" is a place."""

    match = _ORIGIN_COPY.search(value)
    if match is None:
        return False
    place = match.group(1)
    # A place the vocabulary knows, a state code, or a year date the copy.
    return (
        bool(_COUNTRY.search(place))
        or bool(US_STATE_CODE.search(place))
        or bool(re.search(r"\b(?:18|19|20)\d{2}\b", value))
        or any(looks_like_domestic_location(token) for token in re.findall(r"[A-Za-z]{3,}", place))
    )


_LOCATION_INTRO = re.compile(
    r"^\s*in\s+[A-Za-z][A-Za-z'-]+(?:\s*[.,]\s*[A-Za-z][A-Za-z'-]+){1,}\s*$",
    re.I,
)
_WEB_DOMAIN = re.compile(
    r"\b(?:https?://)?(?:www\.)?([a-z0-9][a-z0-9-]{2,62})\."
    r"(?:com|org|net|us|co|io)\b",
    re.I,
)
_DOMAIN_CLASS_SUFFIXES = (
    "distillery",
    "brewery",
    "brewing",
    "winery",
    "spirits",
    "whiskey",
    "whisky",
    "vodka",
    "tequila",
    "brandy",
    "liqueur",
    "bourbon",
    "wine",
    "beer",
    "ale",
    "lager",
    "gin",
    "rum",
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
# Type weight is judged from the stroke width of the heading relative to the body of the
# same statement, both normalized by cap height. Absolute stroke bands do not transfer
# from rendered type to OCR boxes, so only the within-statement ratio is decisive.
_HEADING_BODY_BOLD_RATIO = 1.3
_HEADING_BODY_SAME_RATIO = 1.05
# Below this letter height on the OCR view the stroke estimate is dominated by
# anti-aliasing and the weight ratio is not trusted.
_MIN_RELIABLE_LETTER_HEIGHT = 18.0
# WCAG 2.x contrast ratios: 4.5 is the body-text minimum, 3.0 the large-text minimum.
_CONTRAST_RATIO_PASS_GTE = 4.5
_CONTRAST_RATIO_FAIL_LT = 3.0
# Store lighting, glare, exposure, and compression flatten the contrast a photograph
# records, so a reading between this floor and the 3.0 large-text minimum on type the OCR
# read with confidence is a reviewer's call; below the floor the print is faint beyond what
# capture explains.
_CONTRAST_RATIO_REJECT_LT = 2.0
_LOW_CONTRAST_RANGE = 0.45


def _class_text(value: str) -> str:
    """Expose class words that OCR glued to their neighbours, e.g. "OrganicVodka"."""

    expanded = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", value)
    expanded = re.sub(r"(?<=[A-Za-z])(?=\d)|(?<=\d)(?=[A-Za-z])", " ", expanded)
    # All-capital glue ("GRAPEWINE", "NATURALFLAVORS") is split only where a known
    # qualifier precedes the class word, so ordinary words stay whole.
    expanded = _CAPS_GLUE.sub(r"\1 \2", expanded)
    return re.sub(
        r"\b(wine|beer|ale|lager|vodka|whisk(?:e)?y|rum|gin|tequila)(with|from|by)\b",
        r"\1 \2",
        expanded,
        flags=re.I,
    )


_CAPS_GLUE = re.compile(
    r"\b(grape|table|red|white|rose|dessert|sparkling|fruit|apple|plum|malt|rye|corn|wheat|"
    r"straight|blended|dry|pale|india|amber|imperial|light|natural|artificial)"
    r"(wine|beer|ale|lager|vodka|whisk(?:e)?y|rum|gin|tequila|brandy|flavors?|flavours?|"
    r"spirits?)\b",
    re.I,
)


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
    # A city and state inside the producer's address is not an appellation of origin.
    appellation_lines = [
        item
        for item in ordered
        if not _PRODUCER.search(item.text)
        and not US_STATE_CODE.search(item.text)
        and not _ADDRESS_SHAPE.search(item.text)
    ]
    appellation = _line_candidates(appellation_lines, _APPELLATION, "wine_appellation", factory)
    sulfites = _line_candidates(ordered, _SULFITES, "wine_sulfites", factory)
    # Each panel is read for the statement on its own: a curved bottle or glare can hide
    # part of it in one photograph and show it in the next.
    observations = [
        observation
        for panel in panels
        if panel.panel_id not in unreadable_panel_ids
        and (
            observation := _warning_observation(
                [item for item in ordered if item.panel_id == panel.panel_id],
                panels,
                factory,
                source_unreadable=bool(unreadable_panel_ids),
            )
        ).body
        is not None
    ]
    # A panel with the heading leads; fragments (an edge-cut heading) only ever feed the
    # cross-image read.
    observations.sort(key=lambda item: 0 if item.heading else 1)
    warning = (
        observations[0]
        if observations
        else WarningObservation(source_unreadable=bool(unreadable_panel_ids))
    )
    excluded = {
        item.reading_order
        for item in ordered
        if _line_has_abv(item.text)
        or _PROOF.search(_numeric_scan_text(item.text))
        or _NET.search(_numeric_scan_text(item.text))
        or _class_statement(item.text)
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
    excluded.update(_split_producer_by_orders(ordered))
    excluded.update(_certification_badge_orders(ordered))
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
    return ObservedCandidates(
        fields=fields,
        warning=warning,
        panels=panels,
        evidence=evidence,
        lines=list(ordered),
        warning_alternates=observations[1:],
    )


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


def _candidate_set(items: list[Candidate], key: Callable[[str], str] = casefolded) -> CandidateSet:
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
        value_key = key(item.value)
        current = unique.get(value_key)
        if current is None or (item.evidence.confidence_provenance.signal or 0) > (
            current.evidence.confidence_provenance.signal or 0
        ):
            unique[value_key] = item
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
        scan_text = _numeric_scan_text(line.text)
        for match in pattern.finditer(scan_text):
            value = match.group(0)
            if role == "net_contents":
                # OCR reads the O of "OZ" as a zero on small type; the unit is still ounces.
                value = _ZERO_FOR_O_OUNCE.sub(lambda unit: unit.group(0).replace("0", "O"), value)
                # No label states an empty container: a zero quantity is a misread digit.
                volume = parse_volume_ml(value)
                if volume is not None and volume <= 0:
                    continue
            items.append(Candidate(value=value, evidence=factory.from_line(role, line)))
    if role == "net_contents":
        # "12 FL. OZ" on the front and "12 FL. 0Z" on the side are one statement of one
        # quantity; the readings agree once the volume is parsed.
        return _candidate_set(items, key=_volume_key)
    return _candidate_set(items)


def _volume_key(value: str) -> str:
    volume = parse_volume_ml(value)
    return f"{volume:.1f}" if volume is not None else casefolded(value)


def _abv_candidates(lines: Iterable[OcrLine], factory: _EvidenceFactory) -> CandidateSet:
    items: list[Candidate] = []
    for line in lines:
        scan_text = _numeric_scan_text(line.text)
        percentages = list(_PERCENT.finditer(scan_text))
        contexts = list(_ABV_CONTEXT.finditer(scan_text))
        for match in percentages:
            standalone = re.fullmatch(r"\s*\d{1,3}(?:\.\d+)?\s*%\s*", scan_text) is not None
            contextual = _percent_has_abv_context(scan_text, match, contexts)
            if standalone or contextual:
                items.append(
                    Candidate(value=match.group(0), evidence=factory.from_line("abv", line))
                )
    return _candidate_set(items)


def _line_has_abv(value: str) -> bool:
    scan_text = _numeric_scan_text(value)
    percentages = list(_PERCENT.finditer(scan_text))
    if not percentages:
        return False
    contexts = list(_ABV_CONTEXT.finditer(scan_text))
    if re.fullmatch(r"\s*\d{1,3}(?:\.\d+)?\s*%\s*", scan_text):
        return True
    return any(_percent_has_abv_context(scan_text, percent, contexts) for percent in percentages)


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
    if _BY_VOL_SUFFIX.search(after) or _ALC_PREFIX.search(before):
        return True
    # Compact OCR can merge the entire statement and can confuse one character in
    # "alcohol by volume" (for example, ALCONOLATTOLUME). Requiring both the alcohol
    # prefix and the distinctive volume tail near the percentage remains specific to ABV
    # while recovering these evidence-backed transcriptions.
    nearby = re.sub(
        r"[^a-z0-9]",
        "",
        value[max(0, percent.start() - 24) : percent.end() + 28].lower(),
    )
    return "alc" in nearby and any(token in nearby for token in ("vol", "olume"))


def _numeric_scan_text(value: str) -> str:
    """Expose numeric statement boundaries that OCR visually merged.

    The returned string is used only for pattern matching. Evidence continues to carry the
    exact OCR transcription and original-pixel polygon.
    """

    expanded = _ZERO_FOR_O_OUNCE.sub(
        lambda unit: unit.group(0).replace("0", "O"),
        value,
    )
    expanded = re.sub(
        r"(?<=[0-9%])(?=[A-Za-z])|(?<=[A-Za-z])(?=[0-9])",
        " ",
        expanded,
    )
    expanded = re.sub(r"\balc(?=vol\b)", "ALC ", expanded, flags=re.I)
    expanded = re.sub(r"\bpro0f\b", "PROOF", expanded, flags=re.I)
    return expanded


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
    # A sentence of copy that mentions the class ("a wine with balanced elegance") is not
    # the class statement; a designation set in sentence case ("Blended whisky with
    # natural flavors") is.
    matched = [
        line
        for line in lines
        if _CLASS.search(_class_text(line.text))
        and not _class_copy(line.text)
        and not _WEB_DOMAIN.search(line.text)
    ]
    # A name that carries a class word ("SAISON HOUSE") stays a class candidate beside the
    # line that states the class: the vocabulary cannot know every varietal or type word,
    # so no class-bearing line is dropped, and two readings leave the field to the reviewer.
    strong = [line for line in matched if _STRONG_CLASS.search(_class_text(line.text))]
    preferred = [
        line
        for line in strong
        if not _line_has_abv(line.text)
        and not _NET.search(_numeric_scan_text(line.text))
        and not _PROOF.search(_numeric_scan_text(line.text))
        and not _PRODUCER.search(line.text)
        and not _COUNTRY.search(line.text)
    ]
    selected = preferred or strong or matched
    complete = [line for line in selected if not _INCOMPLETE_CLASS_CONTEXT.search(line.text)]
    if complete:
        selected = complete
    candidate_set = _candidate_set(
        [
            Candidate(
                value=whitespace(_CAPS_GLUE.sub(r"\1 \2", line.text)),
                evidence=factory.from_line("class_type", line),
            )
            for line in selected
        ]
    )
    if candidate_set.status != "Ambiguous":
        return candidate_set
    # Several lines can carry class words for one product ("Kentucky Straight Bourbon
    # Whiskey" on the front and "Whiskey" in a footer). When every reading points to the same
    # beverage family the most specific reading is the designation and the rest are repeats;
    # readings from different families remain a conflict for the reviewer.
    families = {
        family
        for candidate in candidate_set.candidates
        for family in _class_families(candidate.value)
    }
    conflicting = len(families) > 1
    if conflicting or not families:
        return candidate_set
    # Readings of one family are repeats of one designation only when every shorter
    # reading is contained in the fullest one ("Bourbon Whiskey" inside "Kentucky Straight
    # Bourbon Whiskey"). Two designations that name different types of one family
    # ("Blended Whiskey" beside "Straight Bourbon Whiskey") stay a conflict for the reviewer.
    # A composition statement ("100% neutral spirits distilled from ...") describes what the
    # product is made of and never competes with the designation.
    designations = [
        candidate
        for candidate in candidate_set.candidates
        if _designation_shape(candidate.value) >= 0
    ]
    signatures = [_type_signature(candidate.value) for candidate in designations]
    if signatures:
        fullest = max(signatures, key=len)
        if not all(signature <= fullest for signature in signatures):
            return candidate_set
    best = max(
        candidate_set.candidates,
        key=lambda candidate: (
            _designation_shape(candidate.value),
            len(_STRONG_CLASS.findall(_class_text(candidate.value))),
            len(re.findall(r"[A-Za-z]", candidate.value)),
            candidate.evidence.confidence_provenance.signal or 0.0,
        ),
    )
    return CandidateSet(status="Found", candidates=[best])


_COMPOSITION_CONTEXT = re.compile(
    r"(?:\d+\s*%|\b(?:distilled|made|produced|brewed|fermented)\s+(?:from|with)\b|"
    r"\bcontains?\b|\bingredients?\b)",
    re.I,
)


# Words that qualify a class into a type ("straight", "blended", "spiced") or that a
# designation commonly carries; anything else in a class-bearing line is copy.
_TYPE_QUALIFIERS = frozenset(
    [
        "straight",
        "blended",
        "single",
        "malt",
        "light",
        "dry",
        "spiced",
        "flavored",
        "flavoured",
        "white",
        "gold",
        "dark",
        "reposado",
        "anejo",
        "añejo",
        "blanco",
        "extra",
        "overproof",
        "london",
        "table",
        "sparkling",
        "dessert",
        "fortified",
        "brut",
        "ice",
        "pale",
        "india",
        "amber",
        "imperial",
        "wheat",
        "sour",
        "cream",
        "navy",
        "rye",
        "corn",
        "barley",
        "agave",
        "sugar",
        "cane",
        "grape",
        "apple",
        "peach",
        "cherry",
        "coffee",
        "honey",
        "vanilla",
        "cinnamon",
        "citrus",
        "lemon",
        "orange",
        "lime",
        "grapefruit",
        "pineapple",
        "coconut",
        "mango",
        "raspberry",
        "strawberry",
        "blueberry",
        "blackberry",
        "chocolate",
        "mint",
        "ginger",
        "plum",
        "pear",
        "non-alcoholic",
        "nonalcoholic",
        "alcohol-free",
        "blanc",
        "bianco",
        "rosso",
        "rouge",
        "tinto",
        "blanco",
        "rosado",
        # Varietal, type, origin, and finishing words that stand beside a class word in a
        # designation ("Pinot Noir", "Tequila Joven", "finished in port casks").
        "noir",
        "gris",
        "grigio",
        "franc",
        "meunier",
        "nacional",
        "touriga",
        "garnacha",
        "monastrell",
        "mourvedre",
        "mourvèdre",
        "carignan",
        "cinsault",
        "gamay",
        "aligote",
        "aligoté",
        "marsanne",
        "roussanne",
        "torrontes",
        "torrontés",
        "verdejo",
        "godello",
        "mencia",
        "mencía",
        "dolcetto",
        "barbera",
        "aglianico",
        "fiano",
        "greco",
        "falanghina",
        "glera",
        "trebbiano",
        "garganega",
        "corvina",
        "lagrein",
        "zweigelt",
        "furmint",
        "assyrtiko",
        "colombard",
        "muscadet",
        "picpoul",
        "vinho",
        "verde",
        "asti",
        "spumante",
        "frizzante",
        "secco",
        "dolce",
        "amabile",
        "trocken",
        "kabinett",
        "spatlese",
        "spätlese",
        "auslese",
        "eiswein",
        "premier",
        "solera",
        "oloroso",
        "amontillado",
        "fino",
        "manzanilla",
        "tawny",
        "ruby",
        "joven",
        "cristalino",
        "mezcal",
        "artesanal",
        "specialty",
        "specialties",
        "scotch",
        "canadian",
        "japanese",
        "kentucky",
        "tennessee",
        "highland",
        "islay",
        "speyside",
        "lowland",
        "doc",
        "docg",
        "igt",
        "igp",
        "aoc",
        "aop",
        "ava",
        "oak",
        "oaked",
        "unoaked",
        "casks",
        "barrels",
        "mash",
        "wheated",
        "moonshine",
        "unaged",
        "genever",
        "jenever",
        "armagnac",
        "calvados",
        "grappa",
        "pisco",
        "cachaca",
        "cachaça",
        "absinthe",
        "amaro",
        "aperitivo",
        "bitters",
        "schnapps",
        "sake",
        "soju",
        "vsop",
        "napoleon",
    ]
)
_DESIGNATION_FILLER = frozenset(
    [
        "old",
        "aged",
        "years",
        "year",
        "reserve",
        "reserva",
        "premium",
        "small",
        "batch",
        "handcrafted",
        "craft",
        "estate",
        "bottled",
        "bond",
        "cask",
        "strength",
        "distilled",
        "from",
        "with",
        "and",
        "de",
        "of",
        "the",
        "vintage",
        "select",
        "special",
        "original",
        "classic",
        "fine",
        "very",
        "grand",
        "royal",
        "black",
        "blue",
        "red",
        "silver",
        "platinum",
        "gran",
        "cuvee",
        "american",
        "kentucky",
        "tennessee",
        "beverage",
        "beverages",
        "natural",
        "artificial",
        "flavor",
        "flavors",
        "flavour",
        "flavours",
        "color",
        "colour",
        "caramel",
        "added",
        "certified",
        "style",
        "hazy",
        "session",
        "double",
        "triple",
        "belgian",
        "german",
        "bavarian",
        "irish",
        "english",
        "mexican",
        "czech",
        "vienna",
        "munich",
        "helles",
        "export",
        "golden",
        "brown",
        "blonde",
        "blond",
        "milk",
        "oatmeal",
        "pumpkin",
        "farmhouse",
        "barrel",
        "nitro",
        "smoked",
        "sweet",
        "harvest",
        "classico",
        "superiore",
        "riserva",
        "crianza",
        "rosso",
        "bianco",
        "blanc",
        "rouge",
        "tinto",
        "vino",
        "grown",
        "produced",
        "matured",
        "finished",
    ]
)


def _foreign_words(text: str) -> list[str]:
    """Words of a class-bearing line that are neither class words, type qualifiers, nor the
    fillers a designation carries; copy and names are made of them."""

    return [
        token
        for token in re.findall(r"[a-zà-ÿ-]+", text.casefold())
        if len(token) > 3
        and token not in _TYPE_QUALIFIERS
        and token not in _DESIGNATION_FILLER
        and not _CLASS.search(token)
        and not _STRONG_CLASS.search(token)
        and not looks_like_domestic_location(token)
    ]


def _class_statement(value: str) -> bool:
    """A line that states the class or type, as opposed to a name containing a class word.

    "KENTUCKY STRAIGHT BOURBON WHISKEY", "HELLES DOPPELBOCK", and "MALT BEVERAGE WITH
    NATURAL FLAVORS" are designations: the class word heads the line, or every word is
    designation vocabulary, or the line describes composition. "SAISON HOUSE" or "PILSNER
    URQUELL" is a name that happens to carry a style word and stays eligible as the brand.
    """

    text = _class_text(value).strip().rstrip(".,;:!")
    matches = list(_CLASS.finditer(text))
    if not matches or _WEB_DOMAIN.search(value):
        return False
    if _COMPOSITION_CONTEXT.search(text):
        return True
    # The class word heads the designation: whatever follows it is a type or varietal
    # qualifier ("Sauvignon Blanc", "Pinot Noir"), and whatever precedes it may be a region
    # or a producer word that the vocabulary cannot list ("Marlborough Sauvignon Blanc").
    # A name puts a word of its own after the class word ("Saison House").
    if _type_words_only(text[matches[-1].end() :]):
        return True
    if _WINE_FIRST.match(text) and len(_foreign_words(text)) <= 2:
        return True
    # Every word is designation vocabulary: a statement when it runs to three or more words
    # ("Malt beverage with natural flavors") or ends in a type word; a two-word name that
    # puts a filler word after the class word ("Gin Royal", "Bourbon Black") is a name.
    tokens = re.findall(r"[a-zà-ÿ-]+", text.casefold())
    return not _foreign_words(text) and (
        len(tokens) >= 3 or (bool(tokens) and _type_words_only(tokens[-1]))
    )


# Grades a designation carries after its class word ("Chianti Classico Riserva").
_GRADE_WORDS = frozenset(
    ["reserve", "reserva", "riserva", "classico", "superiore", "gran", "grand", "cru", "premier"]
)


def _type_words_only(tail: str) -> bool:
    """Whatever follows the class word is a type qualifier, a class word, or a grade, as in
    "Sauvignon Blanc", "Tequila Joven", or "finished in port casks"; a name puts a word of
    its own there ("Gin Royal", "Bourbon Black", "Saison House")."""

    return all(
        token in _TYPE_QUALIFIERS
        or token in _GRADE_WORDS
        or bool(_CLASS.search(token))
        or bool(_STRONG_CLASS.search(token))
        for token in re.findall(r"[a-zà-ÿ-]+", tail.casefold())
        if len(token) > 3
    )


def _class_copy(value: str) -> bool:
    """A sentence of copy around a class word, as opposed to a designation in sentence case.

    "24 months of aging culminate in a wine with balanced tannins" is copy; "Blended whisky
    with natural flavors" is a designation whose every word is designation vocabulary.
    """

    return _looks_like_prose(value) and bool(_foreign_words(_class_text(value)))


def _designation_shape(value: str) -> int:
    """Prefer a designation whose head word is the class over copy or composition.

    "Organic Vodka" and "Kentucky Straight Bourbon Whiskey" end in the class word and carry
    nothing but the class, its qualifiers, and the usual fillers; "Smooth bourbon whiskey
    experience" is marketing copy around class words; "100% neutral spirits distilled from
    organic sugar cane" describes composition and is the commodity statement rather than
    the class or type designation.
    """

    text = _class_text(value).strip().rstrip(".,;:")
    if _COMPOSITION_CONTEXT.search(text):
        return -1
    tail = re.search(r"(?:\b[\w']+\s*){1,3}$", text)
    if tail is None or not _STRONG_CLASS.search(tail.group(0)):
        return 0
    return 2 if len(_foreign_words(text)) <= 1 else 1


def _type_signature(value: str) -> frozenset[str]:
    """The class words and type qualifiers that define a designation."""

    text = _class_text(value).casefold()
    words = {match.casefold() for match in _STRONG_CLASS.findall(text)}
    words.update(
        token
        for token in re.findall(r"[a-zà-ÿ-]+", text)
        if token in _TYPE_QUALIFIERS and token not in _SIGNATURE_EXCLUDED
    )
    return frozenset(words)


# Origin, appellation, and finishing words describe where or how a type was made, not what
# type it is: "Kentucky Straight Bourbon Whiskey" and "Straight Bourbon Whiskey aged in
# oak" are one designation.
_SIGNATURE_EXCLUDED = frozenset(
    [
        "oak",
        "oaked",
        "unoaked",
        "casks",
        "barrels",
        "kentucky",
        "tennessee",
        "highland",
        "islay",
        "speyside",
        "lowland",
        "doc",
        "docg",
        "igt",
        "igp",
        "aoc",
        "aop",
        "ava",
        "wheated",
        "mash",
        "artesanal",
    ]
)


_CLASS_FAMILIES: dict[str, re.Pattern[str]] = {
    "distilled_spirits": re.compile(
        r"\b(?:bourbon|whisk(?:e)?y|vodka|gin|rum|tequila|brandy|cognac|liqueur|cordial|"
        r"neutral\s+spirits?|grain\s+spirits?|distilled\s+spirits?)\b",
        re.I,
    ),
    "wine": re.compile(
        r"\b(?:wine|merlot|cabernet|chardonnay|pinot|riesling|ros[eé]|sauvignon|zinfandel|"
        r"syrah|shiraz|muscat|sangiovese|malbec|tempranillo|grenache|prosecco|sangria|"
        r"vermouth|port|sherry|champagne|" + _WINE_DESIGNATIONS + r")\b",
        re.I,
    ),
    "malt_beverage": re.compile(
        r"\b(?:malt\s+beverage|beer|ale|lager|stout|porter|pilsner|ipa|india\s+pale\s+ale|"
        r"near\s+beer|cereal\s+beverage|hard\s+seltzer|" + _BEER_STYLES + r")\b",
        re.I,
    ),
}


def _class_families(value: str) -> set[str]:
    text = _class_text(value)
    return {name for name, pattern in _CLASS_FAMILIES.items() if pattern.search(text)}


def _producer_candidates(lines: list[OcrLine], factory: _EvidenceFactory) -> CandidateSet:
    items: list[Candidate] = []
    for index, line in enumerate(lines):
        if index > 0:
            previous = lines[index - 1]
            if (
                previous.panel_id == line.panel_id
                and _PRODUCTION_DESCRIPTOR.fullmatch(whitespace(previous.text))
                and re.match(r"^\s*by\b", line.text, re.I)
                and _same_column(previous, line)
            ):
                # The preceding split role owns this name line. Starting another block here
                # would produce overlapping, ambiguous producer candidates.
                continue
        following = _producer_following_lines(line, lines)
        industry_with_location = bool(
            _INDUSTRY_ORGANIZATION.search(line.text)
            and _industry_location_is_connected(line, following)
        )
        split_role = _is_split_producer_start(line, following)
        if not _PRODUCER.search(line.text) and not industry_with_location and not split_role:
            continue
        group = [line]
        if US_STATE_CODE.search(line.text) or re.search(
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
                pattern.search(_numeric_scan_text(next_line.text))
                for pattern in (_WARNING, _PROOF, _NET)
            ):
                break
            # A company name can carry a weak class word ("Northwind Spirits, Portland,
            # Oregon"); only a strong class designation outside an address ends the block.
            if _STRONG_CLASS.search(
                _class_text(next_line.text)
            ) and not _looks_like_domestic_location(next_line.text):
                break
            group.append(next_line)
            split_name_line = bool(
                split_role and len(group) == 2 and re.match(r"^\s*by\b", next_line.text, re.I)
            )
            if _looks_like_domestic_location(next_line.text) and not split_name_line:
                break
        text = whitespace(" ".join(item.text for item in group))
        items.append(Candidate(value=text, evidence=factory.from_lines("producer", group, text)))
    items = [item for item in items if _producer_is_structured(item.value)]
    items = _drop_contained_candidates(items)
    items.sort(key=lambda item: _producer_candidate_rank(item.value), reverse=True)
    complete = [item for item in items if _producer_candidate_rank(item.value)[0] >= 18]
    if complete:
        # Once a complete role, entity, and location block exists, a bare organization
        # elsewhere on the artwork is not a competing producer statement.
        items = complete
    return _candidate_set(items)


def _producer_following_lines(anchor: OcrLine, lines: list[OcrLine]) -> list[OcrLine]:
    """Return nearby lines below an anchor in its visual column.

    OCR reading order can interleave two label panels printed side by side in one image.
    Producer blocks therefore follow pixel geometry, not list adjacency. The bounded gap
    prevents an organization heading from absorbing unrelated copy farther down a panel.
    """

    anchor_top = min(point.y for point in anchor.polygon)
    anchor_bottom = max(point.y for point in anchor.polygon)
    anchor_height = max(1, anchor_bottom - anchor_top)
    candidates = [
        line
        for line in lines
        if line is not anchor
        and line.panel_id == anchor.panel_id
        and _same_column(anchor, line)
        and min(point.y for point in line.polygon) >= anchor_top - anchor_height // 3
    ]
    candidates.sort(
        key=lambda item: (
            min(point.y for point in item.polygon),
            min(point.x for point in item.polygon),
        )
    )
    selected: list[OcrLine] = []
    previous_bottom = anchor_bottom
    for line in candidates:
        top = min(point.y for point in line.polygon)
        gap_limit = max(90, 3 * max(anchor_height, _line_height(line)))
        if top - previous_bottom > gap_limit:
            break
        selected.append(line)
        previous_bottom = max(previous_bottom, max(point.y for point in line.polygon))
        if len(selected) >= 10:
            break
    return selected


def _producer_candidate_rank(value: str) -> tuple[int, int]:
    """Put a complete role, entity, and location block before incidental entities."""

    score = 0
    if _PRODUCER_ROLE.search(value):
        score += 8
    if _PRODUCER_ENTITY.search(value) or _INDUSTRY_ORGANIZATION.search(value):
        score += 4
    if _looks_like_domestic_location(value) or _COUNTRY_KNOWN_CONTEXT.search(value):
        score += 6
    return score, min(len(value), 500)


def _country_candidates(lines: list[OcrLine], factory: _EvidenceFactory) -> CandidateSet:
    items: list[Candidate] = []
    for line in lines:
        match = _COUNTRY_KNOWN_CONTEXT.search(line.text) or _COUNTRY.search(line.text)
        if match:
            value = whitespace(match.group(1)).rstrip(" .,:;")
            if not value:
                continue
            if is_domestic_origin(value) or (
                not _COUNTRY_NAMES.match(value) and looks_like_domestic_location(value)
            ):
                value = "United States"
            elif not _COUNTRY_NAMES.match(value):
                continue
            items.append(Candidate(value=value, evidence=factory.from_line("country", line)))
    return _candidate_set(items)


def _brand_candidates(
    lines: list[OcrLine], excluded: set[int], factory: _EvidenceFactory
) -> CandidateSet:
    numeric = _numeric_brand_candidate(lines, excluded, factory)
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
        and not _COMPOSITION_CONTEXT.search(line.text)
        and not _COLOR_STATEMENT.search(line.text)
        and not _CODE_PREFIX.match(line.text)
        and not _origin_copy(line.text)
        # A web address is read as a brand only through the domain fallback below.
        and not _WEB_DOMAIN.search(line.text)
        and not _LOCATION_INTRO.search(whitespace(line.text))
        and not _looks_like_domestic_location(line.text)
        and not _PRODUCTION_DESCRIPTOR.fullmatch(whitespace(line.text))
        and re.match(r"^\s*\d+(?:\.\d+)?\s*%", line.text) is None
        and sum(character.isdigit() for character in line.text)
        < sum(character.isalpha() for character in line.text)
        and not _looks_like_ocr_noise(line.text)
        and not _looks_like_prose(line.text)
        and not _looks_like_warning_body_text(line.text)
    ]
    if not eligible:
        return numeric or _domain_brand_candidate(lines, factory)
    horizontal = [line for line in eligible if _is_horizontal_text(line)]
    if horizontal:
        eligible = horizontal
    class_lines = [line for line in lines if _STRONG_CLASS.search(_class_text(line.text))]
    groups = [_brand_group(line, eligible) for line in eligible]
    groups = [
        items
        for items in groups
        if not _looks_like_prose(" ".join(item.text for item in items))
        and not _NON_BRAND_CONTEXT.search(" ".join(item.text for item in items))
        and not _looks_like_warning_body_text(" ".join(item.text for item in items))
    ]
    if not groups:
        return numeric or _domain_brand_candidate(lines, factory)
    tallest = max(_line_height(item) for items in groups for item in items)

    def prominence(items: list[OcrLine]) -> float:
        # The brand is the most prominent non-regulatory text on the brand label. Type size
        # dominates; closeness to the class designation, capitals, and OCR confidence break
        # ties. Nothing here knows any product name.
        height = max(_line_height(item) for item in items) / max(1, tallest)
        associated = any(_near_class_designation(item, class_lines) for item in items)
        text = " ".join(item.text for item in items)
        letters = len(re.findall(r"[A-Za-z]", text))
        confidence = min((item.confidence or 0.0) for item in items)
        return (
            2.5 * height
            + (0.8 if associated else 0.0)
            + (0.3 if text.upper() == text else 0.0)
            + 0.4 * confidence
            + min(0.4, 0.02 * letters)
            - (0.6 if letters <= 3 else 0.0)
        )

    group = max(
        groups,
        key=lambda items: (
            round(prominence(items), 4),
            -min(point.y for point in items[0].polygon),
            -min(point.x for point in items[0].polygon),
            casefolded(whitespace(" ".join(item.text for item in items))),
        ),
    )
    value = _without_trailing_vintage(whitespace(" ".join(item.text for item in group)))
    text_result = CandidateSet(
        status="Found",
        candidates=[Candidate(value=value, evidence=factory.from_lines("brand", group, value))],
    )
    if numeric is None:
        return text_result
    # A numeric mark reaches this point only after the strict context and prominence gate
    # below. Prefer it to an unrelated text fragment such as a translated descriptor. The
    # evidence remains visible, and no filename, upload order, or expected product value is
    # used.
    return numeric


_NUMERIC_MARK = re.compile(r"^\s*(\d{2,5}(?:\s+[A-Z][A-Z0-9'&.-]{1,15})?)\s*[®™]?\s*$", re.I)
_NUMERIC_NON_BRAND_CONTEXT = re.compile(
    r"\b(?:alc|alcohol|vol|proof|ml|lit(?:er|re)?s?|fl\.?\s*oz|ounce|age|aged|years?|"
    r"vintage|harvest|est(?:ablished)?|since|lot|batch|ref|upc|barcode|price|deposit|crv)\b|[$¢%]",
    re.I,
)


def _numeric_brand_candidate(
    lines: list[OcrLine], excluded: set[int], factory: _EvidenceFactory
) -> CandidateSet | None:
    """Return a strongly supported numeric or digit-led brand mark.

    Numeric marks use a separate path so regulatory quantities and dates never enter the
    ordinary text-brand ranker. Geometry, isolation, trademark context, cross-panel
    repetition, and proximity to a class line are the only positive signals.
    """

    candidates: list[tuple[float, OcrLine, str]] = []
    for line in lines:
        text = whitespace(line.text)
        match = _NUMERIC_MARK.fullmatch(text)
        if (
            match is None
            or line.reading_order in excluded
            or (line.confidence or 0.0) < 0.60
            or _NUMERIC_NON_BRAND_CONTEXT.search(text)
            or _ADMINISTRATIVE.search(text)
            or _CODE_PREFIX.match(text)
            or not _is_horizontal_text(line)
            or _numeric_matches_regulatory_value(text, lines)
        ):
            continue
        score = _numeric_brand_score(line, lines)
        if score >= 4.0:
            candidates.append((score, line, match.group(1).strip()))
    if not candidates:
        return None
    candidates.sort(
        key=lambda item: (
            -round(item[0], 4),
            item[1].panel_id,
            min(point.y for point in item[1].polygon),
            min(point.x for point in item[1].polygon),
            item[2].casefold(),
        )
    )
    best_score, best_line, value = candidates[0]
    if len(candidates) > 1 and abs(best_score - candidates[1][0]) < 0.35:
        return CandidateSet(
            status="Ambiguous",
            candidates=[
                Candidate(value=item[2], evidence=factory.from_line("brand", item[1]))
                for item in candidates[:3]
            ],
        )
    return CandidateSet(
        status="Found",
        candidates=[Candidate(value=value, evidence=factory.from_line("brand", best_line))],
    )


def _numeric_brand_score(line: OcrLine, lines: list[OcrLine]) -> float:
    panel_lines = [item for item in lines if item.panel_id == line.panel_id]
    heights = sorted(
        _line_height(item) for item in panel_lines if item is not line and _line_height(item) > 0
    )
    median_height = heights[len(heights) // 2] if heights else 1
    relative_height = min(3.0, _line_height(line) / max(1, median_height))
    class_lines = [item for item in panel_lines if _STRONG_CLASS.search(_class_text(item.text))]
    non_wine_family = any(
        _CLASS_FAMILIES[family].search(_class_text(item.text))
        for family in ("distilled_spirits", "malt_beverage")
        for item in panel_lines
    )
    associated = any(_near_class_designation(line, [item]) for item in class_lines)
    same_value = re.sub(r"\W", "", line.text.casefold())
    repeated = sum(
        1
        for item in lines
        if item.panel_id != line.panel_id
        and re.sub(r"\W", "", item.text.casefold()) == same_value
    )
    ordered = sorted(panel_lines, key=lambda item: item.reading_order)
    position = next((index for index, item in enumerate(ordered) if item is line), -1)
    neighbors = ordered[max(0, position - 1) : position + 2] if position >= 0 else [line]
    trademark = any(_TRADEMARK_MARK.search(item.text) for item in neighbors)
    digits = re.sub(r"\D", "", line.text)
    looks_like_vintage = (
        len(digits) == 4
        and 1800 <= int(digits) <= 2099
        and any(
            _CLASS_FAMILIES["wine"].search(_class_text(item.text))
            or re.search(r"\b(?:vintage|harvest)\b", item.text, re.I)
            for item in panel_lines
        )
        and not trademark
        and not repeated
    )
    year_penalty = 2.5 if looks_like_vintage else 0.0
    return (
        relative_height
        + (1.25 if associated else 0.0)
        + (0.75 if non_wine_family else 0.0)
        + (1.0 if trademark else 0.0)
        + min(1.0, repeated * 0.5)
        + (0.5 if re.fullmatch(r"\s*\d{2,5}\s*[®™]?\s*", line.text) else 0.0)
        - year_penalty
    )


def _numeric_matches_regulatory_value(value: str, lines: list[OcrLine]) -> bool:
    digits = re.sub(r"\D", "", value)
    if not digits:
        return True
    number = float(digits)
    for line in lines:
        for match in _PERCENT.finditer(_numeric_scan_text(line.text)):
            percent = float(match.group(0).replace("%", "").strip())
            if abs(number - percent) < 0.01 or abs(number - 2 * percent) < 0.01:
                return True
        for match in _NET.finditer(_numeric_scan_text(line.text)):
            quantity = re.search(r"\d+(?:\.\d+)?", match.group(0))
            if quantity is not None and abs(number - float(quantity.group(0))) < 0.01:
                return True
    return False


_TRAILING_VINTAGE = re.compile(r"\s*\b(?:18|19|20)\d{2}\b\s*$")


# A trademark mark read as letters is a separate token ("HONEY TM", "HONEY (R)"), never
# the last letters of a word.
_TRADEMARK_MARK = re.compile(r"(?:\s+TM|\s*\(\s*(?:TM|R|SM)\s*\)|\s*[™®℠])\s*$")


def _without_trailing_vintage(value: str) -> str:
    """ "RISERVA 2021" names the vintage after the word, and "HONEY TM" carries a trademark
    mark read as letters; neither is part of the brand."""

    unmarked = _TRADEMARK_MARK.sub("", value)
    stripped = _TRAILING_VINTAGE.sub("", unmarked)
    if (
        len(stripped.split()) < 2
        or not re.search(r"[A-Za-z]{3}", stripped)
        or _INTEGRAL_YEAR.search(unmarked)
    ):
        # "STATION 2000", "VINTAGE 1912", or "OLD NO 1888" is a name with a number in it.
        stripped = unmarked
    return stripped if re.search(r"[A-Za-z]{3}", stripped) else value


_INTEGRAL_YEAR = re.compile(
    r"\b(?:no|n[°º]|of|since|est|anno|the|number)\s*\.?\s+(?:18|19|20)\d{2}\s*$", re.I
)


def _looks_like_ocr_noise(value: str) -> bool:
    letters = [character.casefold() for character in value if character.isalpha()]
    return len(letters) >= 12 and len(set(letters)) <= 3


def _domain_brand_candidate(lines: list[OcrLine], factory: _EvidenceFactory) -> CandidateSet:
    """Use a printed product domain only when no direct brand text survived OCR.

    This is a label-derived fallback, not an online lookup. A beverage-class suffix is
    removed from the domain stem so blueharborvodka.com yields BLUEHARBOR. The source URL
    and its pixel polygon remain visible evidence.
    """

    items: list[Candidate] = []
    for line in lines:
        match = _WEB_DOMAIN.search(line.text)
        if match is None:
            continue
        stem = match.group(1).strip("-").lower()
        for suffix in _DOMAIN_CLASS_SUFFIXES:
            if stem.endswith(suffix) and len(stem) - len(suffix) >= 3:
                stem = stem[: -len(suffix)].rstrip("-")
                break
        value = whitespace(stem.replace("-", " ")).upper()
        if len(re.findall(r"[A-Z]", value)) < 3:
            continue
        items.append(Candidate(value=value, evidence=factory.from_line("brand", line)))
    return _candidate_set(items)


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


def _same_normalized_line(first: str, second: str) -> bool:
    return re.sub(r"[^a-z0-9]", "", first.casefold()) == re.sub(r"[^a-z0-9]", "", second.casefold())


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
    for pattern in (_WARNING, _WARNING_EDGE):
        for index, line in enumerate(lines):
            if pattern.search(line.text):
                return {
                    candidate.reading_order for candidate in _warning_body_lines(lines, index, line)
                }
    return set()


def _warning_body_lines(
    lines: list[OcrLine], heading_index: int, heading: OcrLine
) -> list[OcrLine]:
    heading_bottom = max(point.y for point in heading.polygon)
    heading_height = max(1, _line_height(heading))
    heading_top = min(point.y for point in heading.polygon)
    heading_right = max(point.x for point in heading.polygon)
    spatial = _row_ordered(
        [
            candidate
            for candidate in lines
            if candidate.reading_order != lines[heading_index].reading_order
            and candidate.panel_id == heading.panel_id
            and (
                # The next printed line can start above the heading box's bottom edge when
                # the leading is tight, so anything whose top sits below the heading's
                # midline in the same column belongs to the statement.
                (
                    min(point.y for point in candidate.polygon)
                    >= heading_top + heading_height * 0.5
                    and _same_column(heading, candidate)
                )
                # A box to the right of the heading on the same row carries the start of
                # the body when OCR split the first printed line.
                or (
                    _same_text_row(heading, candidate)
                    and min(point.x for point in candidate.polygon)
                    >= heading_right - heading_height
                )
            )
        ]
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


def _row_ordered(candidates: list[OcrLine]) -> list[OcrLine]:
    """Order lines top to bottom by text row, left to right within a row.

    A curved or split statement often comes back as two boxes per printed line whose tops
    differ by a few pixels; sorting on the raw top coordinate interleaves halves of
    different lines. Boxes that overlap vertically by most of the shorter height share a row.
    """

    rows: list[list[OcrLine]] = []
    for line in sorted(candidates, key=lambda item: min(point.y for point in item.polygon)):
        top = min(point.y for point in line.polygon)
        bottom = max(point.y for point in line.polygon)
        placed = False
        for row in rows:
            row_top = min(min(point.y for point in item.polygon) for item in row)
            row_bottom = max(max(point.y for point in item.polygon) for item in row)
            overlap = min(bottom, row_bottom) - max(top, row_top)
            shorter = max(1, min(bottom - top, row_bottom - row_top))
            if overlap / shorter >= 0.5:
                row.append(line)
                placed = True
                break
        if not placed:
            rows.append([line])
    ordered: list[OcrLine] = []
    for row in rows:
        ordered.extend(sorted(row, key=lambda item: min(point.x for point in item.polygon)))
    return ordered


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


# A line carrying a vintage or establishment year ("RISERVA 2021") is not part of the
# brand name printed above or beside it.
_VINTAGE_YEAR = re.compile(r"\b(?:18|19|20)\d{2}\b")


def _brand_group(first: OcrLine, eligible: list[OcrLine]) -> list[OcrLine]:
    same_row = [
        line
        for line in eligible
        if line is not first
        and line.panel_id == first.panel_id
        and _same_text_row(first, line)
        and len(re.findall(r"[A-Za-z]", line.text)) >= 4
        and not _VINTAGE_YEAR.search(line.text)
        and (line.confidence or 0.0) >= 0.75
        and casefolded(whitespace(line.text)) != casefolded(whitespace(first.text))
    ]
    if same_row:
        return sorted([first, *same_row], key=lambda item: min(point.x for point in item.polygon))
    if len(re.findall(r"[A-Za-z]", first.text)) < 4:
        return [first]
    first_top = min(point.y for point in first.polygon)
    first_bottom = max(point.y for point in first.polygon)
    first_height = _line_height(first)

    def stacked_gap(line: OcrLine) -> int | None:
        """Vertical gap to a line directly below or directly above, else None."""

        top = min(point.y for point in line.polygon)
        bottom = max(point.y for point in line.polygon)
        limit = max(12, min(first_height, _line_height(line)))
        if 0 <= top - first_bottom <= limit:
            return top - first_bottom
        if 0 <= first_top - bottom <= limit:
            return first_top - bottom
        return None

    # A two-line brand ("CRYSTAL" over "TUNDRA", "BOTANIST'S" over "SECRET") is joined from
    # either direction; the partner must be a comparably sized, confidently read line.
    adjacent = [
        line
        for line in eligible
        if line is not first
        and line.panel_id == first.panel_id
        and _same_column(first, line)
        and not _VINTAGE_YEAR.search(line.text)
        and _line_height(line) >= max(10, round(first_height * 0.55))
        and first_height >= max(10, round(_line_height(line) * 0.55))
        and len(re.findall(r"[A-Za-z]", line.text)) >= 4
        and (line.confidence or 0.0) >= 0.7
        and stacked_gap(line) is not None
    ]
    if not adjacent:
        return [first]
    partner = min(
        adjacent,
        key=lambda line: (
            stacked_gap(line) or 0,
            min(point.x for point in line.polygon),
            casefolded(whitespace(line.text)),
        ),
    )
    return sorted([first, partner], key=lambda item: min(point.y for point in item.polygon))


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


def _looks_like_domestic_location(value: str) -> bool:
    return looks_like_domestic_location(value)


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


def _is_split_producer_start(line: OcrLine, following: list[OcrLine]) -> bool:
    if not _PRODUCTION_DESCRIPTOR.fullmatch(whitespace(line.text)):
        return False
    return any(
        candidate.panel_id == line.panel_id
        and _same_column(line, candidate)
        and re.match(r"^\s*by\b", candidate.text, re.I)
        for candidate in following[:2]
    )


def _split_producer_by_orders(lines: list[OcrLine]) -> set[int]:
    excluded: set[int] = set()
    for index, line in enumerate(lines):
        following = lines[index + 1 : index + 3]
        if not _is_split_producer_start(line, following):
            continue
        excluded.add(line.reading_order)
        excluded.update(
            candidate.reading_order
            for candidate in following
            if candidate.panel_id == line.panel_id
            and _same_column(line, candidate)
            and re.match(r"^\s*by\b", candidate.text, re.I)
        )
    return excluded


def _certification_badge_orders(lines: list[OcrLine]) -> set[int]:
    excluded: set[int] = set()
    for first, second in zip(lines, lines[1:], strict=False):
        if first.panel_id != second.panel_id or not _same_column(first, second):
            continue
        pair = (
            re.sub(r"[^a-z]", "", first.text.casefold()),
            re.sub(r"[^a-z]", "", second.text.casefold()),
        )
        if pair in {("gluten", "free"), ("usda", "organic")}:
            excluded.update((first.reading_order, second.reading_order))
    return excluded


def _drop_contained_candidates(items: list[Candidate]) -> list[Candidate]:
    normalized = [(item, casefolded(whitespace(item.value))) for item in items]
    return [
        item
        for item, value in normalized
        if not any(value != other_value and value in other_value for _, other_value in normalized)
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
    # The heading is preferred wherever it sits in reading order; an edge-cut opening
    # anchors a fragment only when no line carries the heading.
    heading_lines = [
        (index, line) for index, line in enumerate(lines) if _WARNING.search(line.text)
    ]
    edge_lines = [
        (index, line) for index, line in enumerate(lines) if _WARNING_EDGE.search(line.text)
    ]
    for index, line in (heading_lines or edge_lines)[:1]:
        heading_match = _WARNING.search(line.text)
        edge_match = None if heading_match else _WARNING_EDGE.search(line.text)
        if heading_match is not None:
            heading, remainder = _warning_heading_and_remainder(line.text, heading_match)
        else:
            assert edge_match is not None
            previous_line = lines[index - 1] if index > 0 else None
            wrapped = (
                re.search(r"government\W*$", previous_line.text, re.I)
                if previous_line is not None
                and previous_line.panel_id == line.panel_id
                and _same_column(previous_line, line)
                else None
            )
            if previous_line is not None and wrapped is not None:
                # The heading wrapped after "GOVERNMENT": both words are in view. Text the
                # OCR merged into that box ahead of the word is not part of the heading.
                heading = whitespace(
                    f"{previous_line.text[wrapped.start() :].strip()} "
                    f"{line.text[: edge_match.end()].strip()}"
                )
            else:
                # An edge-cut heading is not a heading the checks can judge; the line still
                # anchors the statement body, which the cross-image read can complete.
                heading = None
            remainder = line.text[edge_match.end() :].strip()
        body_lines: list[OcrLine] = []
        if remainder:
            body_lines.append(line.model_copy(update={"text": remainder}))
        body_lines.extend(_warning_body_lines(lines, index, line))
        content_lines = [
            candidate for candidate in body_lines if not _looks_like_interruption(candidate.text)
        ]
        body_bold = _body_bold_state(content_lines)
        body = _join_wrapped_lines(content_lines) or None
        heading_evidence = factory.from_line("warning_heading", line) if heading else None
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
        separated = _block_separation(lines, line, body_lines)
        part_two = next(
            (
                body_index
                for body_index, item in enumerate(body_lines)
                if re.search(r"\(?2\)", item.text)
            ),
            None,
        )
        continuity = None
        if part_two is not None:
            interruption = any(_looks_like_interruption(item.text) for item in body_lines)
            continuity = not interruption
        body_weight = _body_weight(content_lines, body_bold, line)
        heading_weight = _heading_weight(
            line,
            content_lines,
            _heading_bold_state(line, previous, content_lines),
            mixed=bool(remainder),
        )
        contrast = _contrast_state(
            line, body_lines, sufficient, _warning_contrast(line, body_lines)
        )
        return WarningObservation(
            heading=heading,
            body=body,
            body_lines=tuple(
                whitespace(item.text) for item in content_lines if whitespace(item.text)
            ),
            full_text=whitespace(f"{heading or ''} {body or ''}"),
            heading_evidence=heading_evidence,
            body_evidence=body_evidence,
            heading_bold=heading_weight,
            body_bold=body_weight,
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


def _weight_ratio(line: OcrLine) -> float | None:
    """Stroke width relative to the measured letter height of the line."""

    if line.stroke_px is None or line.ink_height_px is None or line.ink_height_px < 1:
        return None
    return line.stroke_px / line.ink_height_px


def _weight_measurable(line: OcrLine) -> bool:
    if line.ink_height_px is None or _weight_ratio(line) is None:
        return False
    return line.ink_height_px >= _MIN_RELIABLE_LETTER_HEIGHT


def _body_weight(
    content_lines: list[OcrLine], density_state: bool | None, heading: OcrLine | None = None
) -> bool | None:
    """Body weight from the measured stroke widths, falling back to the ink-density heuristic.

    Stroke widths measured on OCR boxes are comparable within one statement but not
    against an absolute scale, so the body is judged against its own heading: when the
    heading is measurably heavier than the body, the body is regular; a body as heavy as
    its heading is reported as bold for the reviewer; a measurement between the two is
    inconclusive and also goes to the reviewer. The ink-density heuristic decides only when
    no measurement is possible.
    """

    measurable = [item for item in content_lines if _weight_measurable(item)]
    heading_ratio = _weight_ratio(heading) if heading and _weight_measurable(heading) else None
    if len(measurable) >= 2 and heading_ratio is not None:
        ratios = sorted(ratio for item in measurable if (ratio := _weight_ratio(item)) is not None)
        median = ratios[len(ratios) // 2]
        if median > 0:
            relative = heading_ratio / median
            if relative >= _HEADING_BODY_BOLD_RATIO:
                return False
            if relative <= _HEADING_BODY_SAME_RATIO:
                return True
            return None
    return density_state


def _heading_weight(
    heading: OcrLine,
    content_lines: list[OcrLine],
    density_state: bool | None,
    *,
    mixed: bool = False,
) -> bool | None:
    """Heading weight relative to the body of the same statement.

    A heading whose stroke is at least 1.3 times the body stroke, relative to letter
    height, is bold. A heading no heavier than the body is reported for review rather
    than rejected, because the estimator cannot separate a bold heading over a bold body
    from a regular heading over a regular body. A ratio between the two is inconclusive
    and also goes to the reviewer; the ink-density heuristic decides only when no
    measurement is possible.
    """

    # A heading box that also carries the start of the body mixes two weights; its stroke
    # measurement cannot say which part is bold.
    if mixed or not _weight_measurable(heading):
        return density_state
    heading_ratio = _weight_ratio(heading)
    if heading_ratio is None:
        return density_state
    measurable = [item for item in content_lines if _weight_measurable(item)]
    body_ratios = [ratio for item in measurable if (ratio := _weight_ratio(item)) is not None]
    if len(body_ratios) >= 2:
        body_median = sorted(body_ratios)[len(body_ratios) // 2]
        if body_median > 0:
            relative = heading_ratio / body_median
            if relative >= _HEADING_BODY_BOLD_RATIO:
                return True
            if relative <= _HEADING_BODY_SAME_RATIO:
                return False
            return None
    return density_state


def _contrast_state(
    heading: OcrLine,
    body_lines: list[OcrLine],
    sufficient: bool,
    density_state: bool | None,
) -> bool | None:
    """Contrast from two measurements that must agree, else the range heuristic.

    The WCAG luminance ratio between ink and background and the raw gray-level range inside
    the boxes are independent estimators. Both low across at least two lines is faint ink on
    a similar ground; both clear is legible contrast; disagreement, as with a dense or
    inverse-polarity crop, is a review item rather than a verdict either way. A photograph
    cannot establish insufficient contrast on its own when the type reads confidently and
    the ratio sits within capture uncertainty of the minimum: that is a review item.
    """

    content = [item for item in [heading, *body_lines] if not _looks_like_interruption(item.text)]
    measured = [item for item in content if item.contrast_ratio is not None]
    ratios = [item.contrast_ratio for item in measured if item.contrast_ratio is not None]
    if sufficient and len(measured) >= 2 and len(measured) * 2 >= len(content):
        content = measured
        median = sorted(ratios)[len(ratios) // 2]
        ranges = [item.local_contrast for item in content if item.local_contrast is not None]
        range_median = sorted(ranges)[len(ranges) // 2] if ranges else 1.0
        # Anti-aliased type below the measurable letter height dilutes the ink core, so a
        # low reading on small type is not evidence of faint ink.
        heights = [item.ink_height_px for item in content if item.ink_height_px is not None]
        measurable = bool(heights) and sorted(heights)[len(heights) // 2] >= (
            _MIN_RELIABLE_LETTER_HEIGHT
        )
        if (
            measurable
            and len(content) >= 2
            and median < _CONTRAST_RATIO_FAIL_LT
            and range_median < _LOW_CONTRAST_RANGE
        ):
            confidences = [item.confidence for item in content if item.confidence is not None]
            weak_read = (
                bool(confidences) and min(confidences) < (_WARNING_THRESHOLDS["ocrSignalFailLt"])
            )
            if median < _CONTRAST_RATIO_REJECT_LT or weak_read:
                return False
            return None
        if median >= _CONTRAST_RATIO_PASS_GTE and range_median >= _LOW_CONTRAST_RANGE:
            return True
        return None
    # Without the measurements the ink-density heuristic can support a pass or ask for
    # review; it is not evidence enough to reject.
    return (density_state or None) if sufficient else None


def _block_separation(
    lines: list[OcrLine], heading: OcrLine, body_lines: list[OcrLine]
) -> bool | None:
    """Whether other text adjoins the warning block (27 CFR 16.21: separate and apart).

    The block is the heading plus every line read as part of the statement. Any other line on
    the same panel that overlaps the block horizontally is measured above or below it, and a
    line that overlaps it vertically is measured beside it. When nothing adjoins the block it
    is separate; the pass and fail gaps are fractions of the statement's own line height.
    """

    block = [heading, *body_lines]
    left = min(point.x for item in block for point in item.polygon)
    top = min(point.y for item in block for point in item.polygon)
    right = max(point.x for item in block for point in item.polygon)
    bottom = max(point.y for item in block for point in item.polygon)
    heights = sorted(max(1, _line_height(item)) for item in block)
    unit = heights[len(heights) // 2]
    block_orders = {item.reading_order for item in block}
    ratios: list[tuple[float, bool]] = []
    for other in lines:
        if other.panel_id != heading.panel_id or other.reading_order in block_orders:
            continue
        other_left = min(point.x for point in other.polygon)
        other_top = min(point.y for point in other.polygon)
        other_right = max(point.x for point in other.polygon)
        other_bottom = max(point.y for point in other.polygon)
        horizontal = max(0, min(right, other_right) - max(left, other_left))
        vertical = max(0, min(bottom, other_bottom) - max(top, other_top))
        narrower = max(1, min(right - left, other_right - other_left))
        shorter = max(1, min(bottom - top, other_bottom - other_top))
        # The gap is judged against the smaller of the statement's line height and the
        # neighbouring line's height, so a small caption near a large statement still counts.
        comparison = max(1, min(unit, max(1, other_bottom - other_top)))
        # An OCR box far taller than the statement's lines is usually a merged or inflated
        # box whose edges say nothing about ink; it cannot prove that text adjoins the block.
        inflated = (other_bottom - other_top) > unit * 1.8 or (other.confidence or 0.0) < 0.8
        if horizontal / narrower >= 0.25:
            if other_bottom <= top + unit * 0.25:
                ratio = max(0, top - other_bottom) / comparison
            elif other_top >= bottom - unit * 0.25:
                ratio = max(0, other_top - bottom) / comparison
            else:
                ratio = 0.0
        elif vertical / shorter >= 0.3:
            if other_right <= left:
                ratio = (left - other_right) / comparison
            elif other_left >= right:
                ratio = (other_left - right) / comparison
            else:
                ratio = 0.0
        else:
            continue
        ratios.append((ratio, inflated))
    if not ratios:
        return True
    nearest, nearest_inflated = min(ratios, key=lambda item: item[0])
    if nearest >= _WARNING_THRESHOLDS["separationGapPassLineHeightRatioGte"]:
        return True
    if nearest <= _WARNING_THRESHOLDS["separationGapFailLineHeightRatioLte"]:
        return None if nearest_inflated else False
    return None


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
    tokens = re.findall(r"[A-Za-z]+", text.casefold())
    if len(set(tokens) & _WARNING_BODY_WORDS) >= 3:
        return True
    # A short line or a joined pair of fragments that repeats a run of the statement in its
    # order ("or operate", "e machinery and may", "health problems") is a piece of the
    # statement; a name made of the statute's function words ("To the Moon") is not.
    for size in (3, 2):
        for start in range(len(tokens) - size + 1):
            run = tuple(tokens[start : start + size])
            content = sum(1 for word in run if word in _WARNING_BODY_WORDS)
            if run in _STATUTE_RUNS and (size == 3 and content >= 1 or content >= 2):
                return True
    return False


def _contains_warning_like_word(value: str) -> bool:
    tokens = re.findall(r"[A-Za-z]{4,}", value.casefold())
    return any(
        SequenceMatcher(None, token, expected, autojunk=False).ratio() >= 0.72
        for token in tokens
        for expected in _WARNING_BODY_WORDS
    )
