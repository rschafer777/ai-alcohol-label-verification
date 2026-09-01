"""Generate the governed synthetic LabelVerify fixture corpus.

This generator is owned by VV-LEAD. It contains independently authored fixture
and oracle data and does not import production comparison or aggregation code.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import textwrap
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFilter, ImageFont

SCHEMA_VERSION = "1.0.0"
CORPUS_ID = "labelverify-fixtures-v1"
PROFILE_ID = "distilled_spirits_demo_v1"
AUTHORSHIP = "VV-LEAD independent of production comparison and aggregation"
WARNING_BODY = (
    "(1) According to the Surgeon General, women should not drink alcoholic beverages "
    "during pregnancy because of the risk of birth defects. (2) Consumption of alcoholic "
    "beverages impairs your ability to drive a car or operate machinery, and may cause "
    "health problems."
)
SUMMARY_CLEAN = "No differences found in checked fields"
SUMMARY_REVIEW = "Review needed"
SUMMARY_DIFFERENCE = "Differences detected"

CHECK_IDS = [
    "brand",
    "class_type",
    "abv",
    "proof",
    "net_contents",
    "producer",
    "country",
    "warning_applicability",
    "warning_wording",
    "warning_heading_uppercase",
    "warning_heading_emphasis",
    "warning_body_not_bold",
    "warning_separation",
    "warning_continuity",
    "warning_contrast",
    "warning_legibility",
    "warning_physical_size",
    "panel_coverage",
    "image_quality",
]


def reference(**updates: Any) -> dict[str, Any]:
    value: dict[str, Any] = {
        "profileId": PROFILE_ID,
        "caseLabel": None,
        "brandName": "OLD TOM DISTILLERY",
        "classType": "Kentucky Straight Bourbon Whiskey",
        "abvPercent": 45.0,
        "proof": 90.0,
        "netContentsValue": 750.0,
        "netContentsUnit": "mL",
        "producerNameAddress": "OLD TOM DISTILLERY LLC\nFRANKFORT, KENTUCKY 40601",
        "isImported": False,
        "countryOfOrigin": None,
    }
    value.update(updates)
    return value


def override(
    state: str,
    reason: str,
    evidence: str = "required",
    observed: str | None = None,
    alternatives: int = 0,
    applicable: bool = True,
    must_appear: bool = True,
) -> dict[str, Any]:
    return {
        "state": state,
        "reasonClass": reason,
        "evidence": evidence,
        "observedHint": observed,
        "minimumAlternatives": alternatives,
        "applicable": applicable,
        "mustAppear": must_appear,
    }


def result_case(
    case_id: str,
    title: str,
    tags: list[str],
    partition: str = "development",
    ref: dict[str, Any] | None = None,
    visual: dict[str, Any] | None = None,
    panels: list[str] | None = None,
    overrides: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    return {
        "caseId": case_id,
        "title": title,
        "scenarioTags": tags,
        "partition": partition,
        "submissionMode": "ui",
        "expectedKind": "result",
        "reference": ref or reference(),
        "visual": visual or {},
        "panels": panels or ["all"],
        "overrides": overrides or {},
        "fault": None,
    }


def error_case(
    case_id: str,
    title: str,
    tags: list[str],
    code: str,
    http: int,
    panels: list[str],
    fault: str | None = None,
) -> dict[str, Any]:
    return {
        "caseId": case_id,
        "title": title,
        "scenarioTags": tags,
        "partition": "development",
        "submissionMode": "fault_injection" if fault else "api",
        "expectedKind": "error",
        "reference": reference(),
        "visual": {},
        "panels": panels,
        "overrides": {},
        "error": {"code": code, "http": http, "resultMustBeAbsent": True},
        "fault": fault,
    }


def case_specs() -> list[dict[str, Any]]:
    cases = [
        result_case("D001", "Exact clean domestic label", ["exact", "single_panel", "clean"]),
        result_case(
            "D002",
            "Brand case variation routes to review",
            ["brand", "case_variation", "review"],
            ref=reference(brandName="Stone's Throw"),
            visual={"brand": "STONE'S THROW"},
            overrides={"brand": override("Review", "case_variation", observed="STONE'S THROW")},
        ),
        result_case(
            "D003",
            "Brand punctuation and class ambiguity",
            ["brand", "class_type", "punctuation", "ambiguity"],
            visual={"brand": "OLD TOM DISTILLERY.", "classType": "Bourbon Whiskey"},
            overrides={
                "brand": override(
                    "Review", "punctuation_variation", observed="OLD TOM DISTILLERY."
                ),
                "class_type": override("Review", "ambiguous", observed="Bourbon Whiskey"),
            },
        ),
        result_case(
            "D004",
            "Definite brand difference",
            ["brand", "mismatch"],
            visual={"brand": "CLEARWATER RESERVE"},
            overrides={
                "brand": override("Mismatch", "definite_difference", observed="CLEARWATER RESERVE")
            },
        ),
        result_case(
            "D005",
            "Definite class type difference",
            ["class_type", "mismatch"],
            visual={"classType": "Vodka"},
            overrides={"class_type": override("Mismatch", "definite_difference", observed="Vodka")},
        ),
        result_case(
            "D006",
            "ABV proof and net contents differences",
            ["abv", "proof", "net_contents", "mismatch"],
            visual={"abvText": "46% Alc./Vol. (92 Proof)", "netText": "700 mL"},
            overrides={
                "abv": override("Mismatch", "definite_difference", observed="46%"),
                "proof": override("Mismatch", "definite_difference", observed="92 Proof"),
                "net_contents": override("Mismatch", "definite_difference", observed="700 mL"),
            },
        ),
        result_case(
            "D007",
            "Equivalent liter net contents",
            ["net_contents", "safe_equivalence"],
            visual={"netText": "0.75 L"},
            overrides={"net_contents": override("Match", "safe_equivalence", observed="0.75 L")},
        ),
        result_case(
            "D008",
            "Producer punctuation variation",
            ["producer", "punctuation", "review"],
            ref=reference(producerNameAddress="OLD TOM DISTILLERY, LLC\nFRANKFORT, KENTUCKY 40601"),
            visual={"producer": "OLD TOM DISTILLERY LLC\nFRANKFORT KENTUCKY 40601"},
            overrides={
                "producer": override(
                    "Review",
                    "punctuation_variation",
                    observed="OLD TOM DISTILLERY LLC FRANKFORT KENTUCKY 40601",
                )
            },
        ),
        result_case(
            "D009",
            "Imported country exact match",
            ["country", "imported", "multi_panel", "exact"],
            ref=reference(isImported=True, countryOfOrigin="CANADA"),
            visual={"country": "CANADA"},
            panels=["front", "back", "origin"],
            overrides={
                "warning_wording": override("Review", "punctuation_uncertainty")
            },
        ),
        result_case(
            "D010",
            "Conflicting country candidates",
            ["country", "imported", "ambiguity", "multi_panel"],
            ref=reference(isImported=True, countryOfOrigin="CANADA"),
            visual={"countryByPanel": ["CANADA", "UNITED STATES"]},
            panels=["front", "origin:0", "origin:1"],
            overrides={
                "country": override(
                    "Review",
                    "ambiguous",
                    observed="CANADA | UNITED STATES",
                    alternatives=2,
                ),
                "producer": override("Not verified", "missing", evidence="forbidden"),
                "warning_physical_size": override(
                    "Not verified", "unsupported_measurement", evidence="optional"
                ),
                **{
                    check_id: override("Not verified", "missing", evidence="forbidden")
                    for check_id in [
                        "warning_wording",
                        "warning_heading_uppercase",
                        "warning_heading_emphasis",
                        "warning_body_not_bold",
                        "warning_separation",
                        "warning_continuity",
                        "warning_contrast",
                        "warning_legibility",
                    ]
                },
            },
        ),
        result_case(
            "D011",
            "Warning heading uses title case",
            ["warning", "heading_uppercase", "mismatch"],
            visual={"warningHeading": "Government Warning:"},
            overrides={
                "warning_heading_uppercase": override(
                    "Mismatch", "definite_difference", observed="Government Warning:"
                )
            },
        ),
        result_case(
            "D012",
            "Warning heading lacks emphasis",
            ["warning", "heading_emphasis", "review"],
            visual={"headingBold": False},
            overrides={
                "warning_heading_emphasis": override(
                    "Review", "quality_degradation", observed="regular weight"
                )
            },
        ),
        result_case(
            "D013",
            "Warning body is bold",
            ["warning", "body_emphasis", "review"],
            visual={"bodyBold": True},
            overrides={
                "class_type": override("Match", "safe_equivalence"),
                "warning_wording": override("Review", "punctuation_uncertainty"),
                "warning_body_not_bold": override(
                    "Review", "quality_degradation", observed="bold body"
                ),
            },
        ),
        result_case(
            "D014",
            "Warning wording punctuation mutation",
            ["warning", "wording", "punctuation", "mismatch"],
            visual={"warningBody": WARNING_BODY.replace("problems.", "problems!")},
            overrides={
                "warning_wording": override(
                    "Mismatch", "definite_difference", observed="final exclamation mark"
                )
            },
        ),
        result_case(
            "D015",
            "Warning continuity interruption",
            ["warning", "continuity", "mismatch"],
            visual={"continuityBreak": True},
            overrides={
                "warning_continuity": override(
                    "Mismatch", "definite_difference", observed="intervening promotional text"
                )
            },
        ),
        result_case(
            "D016",
            "Warning separation is uncertain",
            ["warning", "separation", "review"],
            visual={"separationUncertain": True},
            overrides={
                "class_type": override("Match", "safe_equivalence"),
                "warning_wording": override("Review", "punctuation_uncertainty"),
                "warning_separation": override(
                    "Review", "ambiguous", observed="adjacent producer text"
                ),
            },
        ),
        result_case(
            "D017",
            "Glare and blur make the label unreadable",
            ["image_quality", "glare", "blur", "unreadable", "negative"],
            visual={"blur": 4.5, "glare": True},
            overrides={
                check_id: override("Not verified", "unreadable", evidence="optional", observed=None)
                for check_id in [
                    "brand",
                    "class_type",
                    "abv",
                    "proof",
                    "net_contents",
                    "producer",
                    "warning_wording",
                    "warning_heading_uppercase",
                    "warning_heading_emphasis",
                    "warning_body_not_bold",
                    "warning_separation",
                    "warning_continuity",
                    "warning_contrast",
                    "warning_legibility",
                    "warning_physical_size",
                ]
            }
            | {
                "panel_coverage": override("Review", "coverage_gap", evidence="optional"),
                "image_quality": override("Not verified", "unreadable", evidence="optional"),
            },
        ),
        result_case(
            "D018",
            "Required back panel is missing",
            ["panel_coverage", "country", "missing", "warning", "negative"],
            ref=reference(isImported=True, countryOfOrigin="CANADA"),
            panels=["front"],
            overrides={
                "country": override("Not verified", "missing", evidence="forbidden"),
                "producer": override("Not verified", "missing", evidence="forbidden"),
                "panel_coverage": override("Not verified", "coverage_gap", evidence="forbidden"),
                "warning_physical_size": override(
                    "Not verified", "unsupported_measurement", evidence="optional"
                ),
                **{
                    check_id: override("Not verified", "missing", evidence="forbidden")
                    for check_id in [
                        "warning_wording",
                        "warning_heading_uppercase",
                        "warning_heading_emphasis",
                        "warning_body_not_bold",
                        "warning_separation",
                        "warning_continuity",
                        "warning_contrast",
                        "warning_legibility",
                    ]
                },
            },
        ),
        error_case(
            "D019",
            "Corrupt PNG fails closed",
            ["invalid_image", "corrupt", "negative"],
            "invalid_image",
            422,
            ["corrupt_png"],
        ),
        error_case(
            "D020",
            "Unsupported GIF fails closed",
            ["unsupported_media", "negative"],
            "unsupported_media_type",
            415,
            ["unsupported_gif"],
        ),
        error_case(
            "D021",
            "Zero panels fails validation",
            ["panel_count", "zero", "negative"],
            "invalid_panel_count",
            422,
            [],
        ),
        error_case(
            "D022",
            "Seven panels exceeds the contract",
            ["panel_count", "maximum", "negative"],
            "multipart_limit_exceeded",
            413,
            ["front"] * 7,
        ),
        error_case(
            "D023",
            "Decoded pixel limit fails closed",
            ["pixel_limit", "resource_boundary", "negative"],
            "decoded_pixel_limit",
            422,
            ["oversize_pixels"],
        ),
        error_case(
            "D024",
            "Controlled inference timeout returns no result",
            ["inference_timeout", "fault_injection", "negative"],
            "inference_timeout",
            504,
            ["all"],
            fault="inference_timeout",
        ),
        result_case(
            "H001",
            "Six panel exact holdout",
            ["exact", "six_panel", "holdout", "clean"],
            partition="holdout",
            panels=["front", "back", "details", "scale", "side", "side"],
            overrides={
                "warning_wording": override("Review", "punctuation_uncertainty")
            },
        ),
        result_case(
            "H002",
            "Expected proof is missing",
            ["proof", "missing", "holdout"],
            partition="holdout",
            visual={"abvText": "45% Alc./Vol."},
            overrides={"proof": override("Not verified", "missing", evidence="forbidden")},
        ),
        result_case(
            "H003",
            "Imported origin and producer differ",
            ["country", "producer", "mismatch", "holdout"],
            partition="holdout",
            ref=reference(isImported=True, countryOfOrigin="CANADA"),
            visual={
                "country": "FRANCE",
                "producer": "RIVER ROAD IMPORTS\nLOUISVILLE, KENTUCKY 40202",
            },
            panels=["front", "back", "origin"],
            overrides={
                "country": override("Mismatch", "definite_difference", observed="FRANCE"),
                "warning_wording": override("Review", "punctuation_uncertainty"),
                "producer": override(
                    "Mismatch",
                    "definite_difference",
                    observed="RIVER ROAD IMPORTS LOUISVILLE KENTUCKY 40202",
                ),
            },
        ),
        result_case(
            "H004",
            "Warning has low contrast",
            ["warning", "contrast", "legibility", "holdout"],
            partition="holdout",
            visual={"warningFill": 205},
            overrides={
                "class_type": override("Match", "safe_equivalence"),
                "warning_wording": override("Review", "punctuation_uncertainty"),
                "warning_contrast": override(
                    "Mismatch", "definite_difference", observed="low contrast"
                ),
                "warning_legibility": override(
                    "Review", "quality_degradation", observed="difficult to read"
                ),
            },
        ),
        result_case(
            "H005",
            "Physical warning size cannot be verified",
            ["warning", "physical_size", "holdout", "human_confirmation"],
            partition="holdout",
            visual={"reliableScale": False},
            overrides={
                "class_type": override("Match", "safe_equivalence"),
                "warning_wording": override("Review", "punctuation_uncertainty"),
                "warning_physical_size": override(
                    "Not verified", "unsupported_measurement", evidence="optional"
                ),
            },
        ),
        result_case(
            "H006",
            "Warning is not applicable below threshold",
            ["warning_applicability", "not_applicable", "holdout"],
            partition="holdout",
            ref=reference(abvPercent=0.4, proof=0.8),
            visual={"abvText": "0.4% Alc./Vol. (0.8 Proof)", "omitWarning": True},
            overrides={"class_type": override("Match", "safe_equivalence")},
        ),
    ]
    assert len(cases) == 30
    return cases


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def contract_hashes(project_root: Path) -> dict[str, str]:
    names = [
        "api-contract-v1.json",
        "error-registry-v1.json",
        "selected-check-registry-v1.json",
        "regulatory-rules-v1.json",
    ]
    return {name: sha256(project_root / "contracts" / name) for name in names}


def check_expectations(spec: dict[str, Any]) -> list[dict[str, Any]]:
    ref = spec["reference"]
    warning_applicable = float(ref["abvPercent"]) >= 0.5
    country_applicable = bool(ref["isImported"])
    expectations: dict[str, dict[str, Any]] = {}
    for check_id in CHECK_IDS:
        applicable = True
        must_appear = True
        reason = "exact"
        evidence = "required"
        state = "Match"
        if check_id == "country" and not country_applicable:
            applicable = False
            must_appear = False
            reason = "not_applicable"
            evidence = "forbidden"
            state = "Not verified"
        if (
            check_id.startswith("warning_")
            and check_id != "warning_applicability"
            and not warning_applicable
        ):
            applicable = False
            must_appear = False
            reason = "not_applicable"
            evidence = "forbidden"
            state = "Not verified"
        if check_id == "warning_physical_size" and warning_applicable:
            expectations[check_id] = override(
                "Not verified", "unsupported_measurement", evidence="optional"
            )
            continue
        if check_id in {"panel_coverage", "image_quality"}:
            evidence = "optional"
        if check_id == "warning_applicability":
            evidence = "optional"
        expectations[check_id] = override(
            state,
            reason,
            evidence=evidence,
            applicable=applicable,
            must_appear=must_appear,
        )
    for check_id, expected in spec["overrides"].items():
        expectations[check_id] = expected
    return [{"checkId": check_id, **expectations[check_id]} for check_id in CHECK_IDS]


def summary_for(checks: list[dict[str, Any]]) -> str:
    applicable = [row for row in checks if row["applicable"]]
    if any(row["state"] == "Mismatch" for row in applicable):
        return SUMMARY_DIFFERENCE
    if any(row["state"] in {"Review", "Not verified"} for row in applicable):
        return SUMMARY_REVIEW
    return SUMMARY_CLEAN


def oracle_for(spec: dict[str, Any]) -> dict[str, Any]:
    base = {
        "schemaVersion": SCHEMA_VERSION,
        "oracleId": f"oracle_{spec['caseId'].lower()}",
        "caseId": spec["caseId"],
        "authorship": AUTHORSHIP,
        "outcomeKind": spec["expectedKind"],
        "notes": [
            "Expected values are authored in the fixture generator, not imported from production.",
            "Non-applicable rows remain in the oracle with mustAppear false.",
        ],
    }
    if spec["expectedKind"] == "error":
        base["error"] = spec["error"]
        return base
    checks = check_expectations(spec)
    base["checks"] = checks
    base["summary"] = summary_for(checks)
    return base


def text_lines(spec: dict[str, Any], section: str) -> list[tuple[str, bool, int]]:
    ref = spec["reference"]
    visual = spec["visual"]
    brand = visual.get("brand", ref["brandName"])
    class_type = visual.get("classType", ref["classType"])
    abv_text = visual.get(
        "abvText",
        f"{ref['abvPercent']:g}% Alc./Vol."
        + (f" ({ref['proof']:g} Proof)" if ref.get("proof") is not None else ""),
    )
    net_text = visual.get("netText", f"{ref['netContentsValue']:g} {ref['netContentsUnit']}")
    producer = visual.get("producer", ref["producerNameAddress"])
    warning_heading = visual.get("warningHeading", "GOVERNMENT WARNING:")
    warning_body = visual.get("warningBody", WARNING_BODY)
    warning_fill = int(visual.get("warningFill", 20))
    lines: list[tuple[str, bool, int]] = [("SYNTHETIC TEST LABEL", True, 20)]
    if section in {"all", "front"}:
        lines.extend(
            [
                (brand, True, 20),
                (class_type, False, 20),
                (abv_text, False, 20),
                (net_text, False, 20),
            ]
        )
    if section in {"all", "back"}:
        lines.extend((line, False, 20) for line in producer.splitlines())
        if not visual.get("omitWarning", False):
            if visual.get("separationUncertain", False):
                lines.append(("BOTTLED FOR TEST REVIEW", False, warning_fill))
            lines.append((warning_heading, bool(visual.get("headingBold", True)), warning_fill))
            first, second = warning_body.split("(2)", maxsplit=1)
            lines.append((first.strip(), bool(visual.get("bodyBold", False)), warning_fill))
            if visual.get("continuityBreak", False):
                lines.append(("OLD TOM QUALITY SINCE 1998", True, warning_fill))
            lines.append(("(2)" + second, bool(visual.get("bodyBold", False)), warning_fill))
    if section == "details":
        lines.extend([("LOT: SYNTHETIC-001", False, 20), (net_text, False, 20)])
    if section == "scale":
        lines.extend([("REFERENCE SCALE", True, 20), ("2 mm", False, 20)])
    if section == "side":
        lines.append(("SYNTHETIC SIDE PANEL", False, 20))
    if section.startswith("origin"):
        if "countryByPanel" in visual:
            index = int(section.split(":", maxsplit=1)[1])
            country = visual["countryByPanel"][index]
        else:
            country = visual.get("country", ref.get("countryOfOrigin"))
        lines.append((f"PRODUCT OF {country}", True, 20))
    if visual.get("reliableScale", True) and section in {"all", "back", "scale"}:
        lines.append(("SYNTHETIC SCALE: 2 mm", False, 20))
    return lines


def render_panel(spec: dict[str, Any], section: str, path: Path) -> None:
    if section == "corrupt_png":
        path.write_bytes(b"\x89PNG\r\n\x1a\ninvalid png fixture body\x00\x01")
        return
    width, height = (4001, 3000) if section == "oversize_pixels" else (1200, 1600)
    image = Image.new("RGB", (width, height), (248, 244, 232))
    draw = ImageDraw.Draw(image)
    margin = max(35, width // 30)
    draw.rounded_rectangle(
        (margin, margin, width - margin, height - margin),
        radius=24,
        outline=(45, 38, 30),
        width=max(3, width // 400),
    )
    font_title = ImageFont.load_default(size=max(24, width // 30))
    font_body = ImageFont.load_default(size=max(20, width // 40))
    y = margin + 35
    rendered_section = "all" if section == "oversize_pixels" else section
    for text, bold, fill_value in text_lines(spec, rendered_section):
        font = font_title if bold else font_body
        wrap_width = 48 if width == 1200 else 110
        for wrapped in textwrap.wrap(text, width=wrap_width) or [""]:
            fill = (fill_value, fill_value, fill_value)
            draw.text((margin + 35, y), wrapped, font=font, fill=fill)
            if bold:
                draw.text((margin + 37, y), wrapped, font=font, fill=fill)
            y += int(font.size * 1.35)
        y += int(font.size * 0.35)
    if spec["visual"].get("glare", False):
        overlay = Image.new("RGBA", image.size, (255, 255, 255, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        overlay_draw.polygon(
            [(width // 3, 0), (2 * width // 3, 0), (width, height), (2 * width // 3, height)],
            fill=(255, 255, 255, 190),
        )
        image = Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB")
    blur = float(spec["visual"].get("blur", 0))
    if blur:
        image = image.filter(ImageFilter.GaussianBlur(radius=blur))
    if section == "unsupported_gif":
        image.save(path, format="GIF")
    else:
        image.save(path, format="PNG", compress_level=9, optimize=False)


def mime_for(section: str) -> str:
    if section == "unsupported_gif":
        return "image/gif"
    return "image/png"


def extension_for(section: str) -> str:
    return ".gif" if section == "unsupported_gif" else ".png"


def generate_case(
    fixtures_root: Path, spec: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any]]:
    partition = spec["partition"]
    case_id = spec["caseId"]
    case_root = fixtures_root / partition / "cases" / case_id
    panels_root = case_root / "panels"
    panels_root.mkdir(parents=True, exist_ok=True)
    reference_path = case_root / "reference.json"
    write_json(reference_path, spec["reference"])
    panel_records = []
    for index, section in enumerate(spec["panels"], start=1):
        panel_id = f"panel-{index}"
        panel_path = panels_root / f"{panel_id}{extension_for(section)}"
        render_panel(spec, section, panel_path)
        width: int | None = None
        height: int | None = None
        if section != "corrupt_png":
            with Image.open(panel_path) as image:
                width, height = image.size
        panel_records.append(
            {
                "panelId": panel_id,
                "path": panel_path.relative_to(fixtures_root.parent).as_posix(),
                "mimeType": mime_for(section),
                "sha256": sha256(panel_path),
                "bytes": panel_path.stat().st_size,
                "width": width,
                "height": height,
            }
        )
    oracle = oracle_for(spec)
    oracle_path = fixtures_root / "oracle" / partition / f"{case_id}.json"
    write_json(oracle_path, oracle)
    record = {
        "caseId": case_id,
        "partition": partition,
        "sealed": partition == "holdout",
        "title": spec["title"],
        "scenarioTags": spec["scenarioTags"],
        "submissionMode": spec["submissionMode"],
        "expectedKind": spec["expectedKind"],
        "referencePath": reference_path.relative_to(fixtures_root.parent).as_posix(),
        "oraclePath": oracle_path.relative_to(fixtures_root.parent).as_posix(),
        "panels": panel_records,
        "fault": spec["fault"],
    }
    write_json(case_root / "case-manifest.json", record)
    return record, oracle


def sample_spec() -> dict[str, Any]:
    return result_case(
        "S001",
        "Old Tom deterministic sample",
        ["sample", "exact", "two_panel", "review"],
        panels=["front", "back"],
        overrides={
            "warning_wording": override("Review", "punctuation_uncertainty")
        },
    )


def generate_sample(fixtures_root: Path, hashes: dict[str, str]) -> dict[str, Any]:
    spec = sample_spec()
    sample_root = fixtures_root / "sample"
    panels_root = sample_root / "panels"
    panels_root.mkdir(parents=True, exist_ok=True)
    reference_path = sample_root / "reference.json"
    write_json(reference_path, spec["reference"])
    panels = []
    for index, section in enumerate(spec["panels"], start=1):
        panel_path = panels_root / f"panel-{index}.png"
        render_panel(spec, section, panel_path)
        with Image.open(panel_path) as image:
            width, height = image.size
        panels.append(
            {
                "panelId": f"panel-{index}",
                "path": panel_path.relative_to(fixtures_root.parent).as_posix(),
                "mimeType": "image/png",
                "sha256": sha256(panel_path),
                "bytes": panel_path.stat().st_size,
                "width": width,
                "height": height,
            }
        )
    oracle = oracle_for(spec)
    oracle_path = fixtures_root / "oracle" / "sample" / "S001.json"
    write_json(oracle_path, oracle)
    manifest = {
        "sampleContractVersion": SCHEMA_VERSION,
        "sampleId": "old-tom-distillery-v1",
        "caseId": "S001",
        "profileId": PROFILE_ID,
        "displayName": "Old Tom Distillery synthetic sample",
        "syntheticOnly": True,
        "contractHashes": hashes,
        "referencePath": reference_path.relative_to(fixtures_root.parent).as_posix(),
        "reference": spec["reference"],
        "panels": panels,
        "oraclePath": oracle_path.relative_to(fixtures_root.parent).as_posix(),
        "expectedSummary": oracle["summary"],
    }
    write_json(sample_root / "sample-manifest-v1.json", manifest)
    return manifest


def mutation_plan() -> dict[str, Any]:
    rows = [
        {
            "mutationId": "M001_case_id_rename",
            "sourceCaseId": "D001",
            "operation": "rename_case_id",
            "target": "caseId",
            "value": "RANDOMIZED_CASE",
            "expectedChangedChecks": [],
            "expectedSummary": SUMMARY_REVIEW,
            "invariant": "Results must not depend on fixture ID.",
        },
        {
            "mutationId": "M002_panel_order",
            "sourceCaseId": "H001",
            "operation": "reverse_panels",
            "target": "panels",
            "value": None,
            "expectedChangedChecks": [],
            "expectedSummary": SUMMARY_REVIEW,
            "invariant": "Evidence panel IDs may change but machine states must not.",
        },
        {
            "mutationId": "M003_brand_text",
            "sourceCaseId": "D001",
            "operation": "replace_label_text",
            "target": "brand",
            "value": "RANDOM HARBOR",
            "expectedChangedChecks": ["brand"],
            "expectedSummary": SUMMARY_DIFFERENCE,
            "invariant": "A semantic brand mutation must change the brand result.",
        },
        {
            "mutationId": "M004_warning_case",
            "sourceCaseId": "D001",
            "operation": "replace_label_text",
            "target": "warning_heading_uppercase",
            "value": "Government Warning:",
            "expectedChangedChecks": ["warning_heading_uppercase"],
            "expectedSummary": SUMMARY_DIFFERENCE,
            "invariant": "Warning capitalization cannot be inferred from the fixture name.",
        },
        {
            "mutationId": "M005_country_conflict",
            "sourceCaseId": "D009",
            "operation": "add_conflicting_candidate",
            "target": "country",
            "value": "UNITED STATES",
            "expectedChangedChecks": ["country"],
            "expectedSummary": SUMMARY_REVIEW,
            "invariant": "Reference value cannot choose among conflicting observed candidates.",
        },
        {
            "mutationId": "M006_reference_abv",
            "sourceCaseId": "D001",
            "operation": "replace_reference_value",
            "target": "abvPercent",
            "value": 46.0,
            "expectedChangedChecks": ["abv", "proof"],
            "expectedSummary": SUMMARY_DIFFERENCE,
            "invariant": "Observed OCR must remain unchanged when only reference data changes.",
        },
        {
            "mutationId": "M007_remove_warning_panel",
            "sourceCaseId": "D009",
            "operation": "remove_panel",
            "target": "back",
            "value": None,
            "expectedChangedChecks": [
                "producer",
                "warning_wording",
                "warning_heading_uppercase",
                "warning_heading_emphasis",
                "warning_body_not_bold",
                "warning_separation",
                "warning_continuity",
                "warning_contrast",
                "warning_legibility",
            ],
            "expectedSummary": SUMMARY_REVIEW,
            "invariant": "Missing evidence cannot remain Match or clean.",
        },
        {
            "mutationId": "M008_image_blur",
            "sourceCaseId": "D001",
            "operation": "apply_blur",
            "target": "all_panels",
            "value": 6.0,
            "expectedChangedChecks": [
                "brand",
                "class_type",
                "abv",
                "proof",
                "net_contents",
                "producer",
                "warning_wording",
                "warning_heading_uppercase",
                "warning_heading_emphasis",
                "warning_body_not_bold",
                "warning_separation",
                "warning_continuity",
                "warning_contrast",
                "warning_legibility",
                "warning_physical_size",
                "panel_coverage",
                "image_quality",
            ],
            "expectedSummary": SUMMARY_REVIEW,
            "invariant": (
                "Material degradation must affect quality and cannot create a clean result."
            ),
        },
    ]
    return {"schemaVersion": SCHEMA_VERSION, "mutations": rows}


def write_holdout_seal(fixtures_root: Path, holdout_records: list[dict[str, Any]]) -> None:
    paths: set[Path] = set()
    for record in holdout_records:
        paths.add(fixtures_root.parent / record["referencePath"])
        paths.add(fixtures_root.parent / record["oraclePath"])
        paths.add(fixtures_root / "holdout" / "cases" / record["caseId"] / "case-manifest.json")
        for panel in record["panels"]:
            paths.add(fixtures_root.parent / panel["path"])
    lines = [
        f"{sha256(path)}  {path.relative_to(fixtures_root).as_posix()}"
        for path in sorted(paths, key=lambda item: item.as_posix())
    ]
    (fixtures_root / "holdout" / "SEAL.sha256").write_text(
        "\n".join(lines) + "\n", encoding="ascii", newline="\n"
    )


def generate(output_root: Path, project_root: Path) -> dict[str, Any]:
    output_root.mkdir(parents=True, exist_ok=True)
    hashes = contract_hashes(project_root)
    records = []
    oracles = []
    for spec in case_specs():
        record, oracle = generate_case(output_root, spec)
        records.append(record)
        oracles.append(oracle)
    development = [record for record in records if record["partition"] == "development"]
    holdout = [record for record in records if record["partition"] == "holdout"]
    manifest = {
        "schemaVersion": SCHEMA_VERSION,
        "corpusId": CORPUS_ID,
        "contractHashes": hashes,
        "developmentCount": len(development),
        "holdoutCount": len(holdout),
        "cases": records,
    }
    write_json(output_root / "corpus-manifest-v1.json", manifest)
    write_json(
        output_root / "development" / "manifest-v1.json",
        {"schemaVersion": SCHEMA_VERSION, "partition": "development", "cases": development},
    )
    write_json(
        output_root / "holdout" / "manifest-sealed-v1.json",
        {
            "schemaVersion": SCHEMA_VERSION,
            "partition": "holdout",
            "sealed": True,
            "sealedBy": "VV-LEAD",
            "cases": holdout,
        },
    )
    write_json(
        output_root / "oracle" / "corpus-oracle-index-v1.json",
        {
            "schemaVersion": SCHEMA_VERSION,
            "authorship": AUTHORSHIP,
            "oracles": [
                {
                    "caseId": oracle["caseId"],
                    "path": next(
                        record["oraclePath"]
                        for record in records
                        if record["caseId"] == oracle["caseId"]
                    ),
                    "sha256": sha256(
                        output_root.parent
                        / next(
                            record["oraclePath"]
                            for record in records
                            if record["caseId"] == oracle["caseId"]
                        )
                    ),
                }
                for oracle in oracles
            ],
        },
    )
    write_json(output_root / "mutations" / "mutation-plan-v1.json", mutation_plan())
    generate_sample(output_root, hashes)
    write_holdout_seal(output_root, holdout)
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    project_root = Path(__file__).resolve().parents[1]
    output = args.output.resolve() if args.output else project_root / "fixtures"
    manifest = generate(output, project_root)
    print(
        json.dumps(
            {
                "corpusId": manifest["corpusId"],
                "developmentCount": manifest["developmentCount"],
                "holdoutCount": manifest["holdoutCount"],
                "totalCount": len(manifest["cases"]),
                "output": str(output),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
