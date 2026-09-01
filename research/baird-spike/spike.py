from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import re
import threading
import time
from pathlib import Path

import cv2
import numpy as np
import psutil
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
from rapidocr import RapidOCR
from rapidocr.utils.typings import LangDet, LangRec


ROOT = Path(__file__).resolve().parent
FIXTURES = ROOT / "fixtures"
RESULTS = ROOT / "results"
FIXTURES.mkdir(exist_ok=True)
RESULTS.mkdir(exist_ok=True)

FONT_REGULAR = r"C:\Windows\Fonts\arial.ttf"
FONT_BOLD = r"C:\Windows\Fonts\arialbd.ttf"
CHECK_REGISTRY_PATH = Path(os.environ.get("LABELVERIFY_CHECK_REGISTRY_PATH", ROOT / "selected-check-registry.json"))
REGULATORY_RULES_PATH = Path(os.environ.get("LABELVERIFY_REGULATORY_RULES_PATH", ROOT / "regulatory-rules.json"))
EXPECTED_MANIFEST_PATH = ROOT / "expected-field-manifest.json"
CHECK_REGISTRY = json.loads(CHECK_REGISTRY_PATH.read_text(encoding="utf-8"))
REGULATORY_RULES = json.loads(REGULATORY_RULES_PATH.read_text(encoding="utf-8"))
EXPECTED_MANIFEST = json.loads(EXPECTED_MANIFEST_PATH.read_text(encoding="utf-8"))
ALL_CHECK_IDS = tuple(check["check_id"] for check in CHECK_REGISTRY["checks"])
WARNING_HEADING = REGULATORY_RULES["warning"]["heading_exact"]
WARNING_BODY = REGULATORY_RULES["warning"]["body_exact"]
WARNING_THRESHOLD = float(REGULATORY_RULES["warning"]["applicability_abv_percent_gte"])


def ocr_params() -> dict:
    params = {
        "Rec.lang_type": LangRec.EN,
        "Det.lang_type": LangDet.EN,
        "EngineConfig.onnxruntime.intra_op_num_threads": 2,
        "EngineConfig.onnxruntime.inter_op_num_threads": 1,
        "EngineConfig.onnxruntime.enable_cpu_mem_arena": False,
        "Global.log_level": "error",
        "Global.font_path": FONT_REGULAR,
        "Global.max_side_len": 3000,
        "Det.limit_side_len": 1600,
    }
    model_root_value = os.environ.get("LABELVERIFY_MODEL_ROOT")
    if model_root_value:
        model_root = Path(model_root_value)
        params.update({
            "Det.model_path": str(model_root / "en_PP-OCRv3_det_infer.onnx"),
            "Rec.model_path": str(model_root / "en_PP-OCRv4_rec_infer.onnx"),
            "Cls.model_path": str(model_root / "ch_ppocr_mobile_v2.0_cls_infer.onnx"),
        })
    return params


def font(size: int, bold: bool = False):
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REGULAR, size)


def wrap(draw: ImageDraw.ImageDraw, text: str, fnt, max_width: int) -> list[str]:
    words = text.split()
    lines, current = [], ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if draw.textbbox((0, 0), candidate, font=fnt)[2] <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def panel(lines, size=(1200, 1800), glare=False, blur=0.0, text_fill="#151515") -> Image.Image:
    im = Image.new("RGB", size, "#e6e1d4")
    draw = ImageDraw.Draw(im)
    margin = int(size[0] * 0.08)
    draw.rounded_rectangle((margin, margin, size[0] - margin, size[1] - margin), 24, fill="#fbf8ed", outline="#29261f", width=6)
    y = margin + 70
    for entry in lines:
        text, point_size, bold = entry[:3]
        line_fill = entry[3] if len(entry) > 3 else text_fill
        if text is None:
            y += int(point_size)
            continue
        fnt = font(point_size, bold)
        for line in wrap(draw, text, fnt, size[0] - 2 * margin - 80):
            draw.text((margin + 40, y), line, font=fnt, fill=line_fill)
            y += int(point_size * 1.28)
        y += int(point_size * 0.35)
    if glare:
        overlay = Image.new("RGBA", size, (0, 0, 0, 0))
        od = ImageDraw.Draw(overlay)
        od.polygon([(680, 0), (920, 0), (500, size[1]), (270, size[1])], fill=(255, 255, 255, 155))
        im = Image.alpha_composite(im.convert("RGBA"), overlay).convert("RGB")
    if blur:
        im = im.filter(ImageFilter.GaussianBlur(blur))
    return im


def base_lines(brand="OLD TOM DISTILLERY", abv="45% Alc./Vol. (90 Proof)", warning_heading="GOVERNMENT WARNING:", warning_body=WARNING_BODY, producer="OLD HERITAGE DISTILLERY, LLC", heading_bold=True, body_bold=False):
    return [
        (brand, 82, True), ("Kentucky Straight Bourbon Whiskey", 48, True),
        (abv, 47, False), ("750 mL", 47, False), (warning_heading, 43, heading_bold),
        (warning_body, 31, body_bold), (f"BOTTLED BY: {producer}", 32, True),
        ("FRANKFORT, KENTUCKY 40601", 32, False),
    ]


def save_case(case_id, panels, reference, tags):
    paths, case_dir = [], FIXTURES / case_id
    case_dir.mkdir(exist_ok=True)
    for i, im in enumerate(panels, 1):
        path = case_dir / f"panel-{i}.jpg"
        im.save(path, "JPEG", quality=90, optimize=True)
        paths.append(path.relative_to(ROOT).as_posix())
    return {
        "case_id": case_id,
        "paths": paths,
        "reference": reference,
        "expected_summary": EXPECTED_MANIFEST["cases"][case_id]["summary"],
        "tags": tags,
    }


def make_cases():
    ref = {
        "brand": "OLD TOM DISTILLERY", "class_type": "Kentucky Straight Bourbon Whiskey",
        "abv": "45%", "proof": "90", "net_contents": "750 mL",
        "producer": "OLD HERITAGE DISTILLERY, LLC FRANKFORT, KENTUCKY 40601",
        "country": None, "warning": "GOVERNMENT WARNING: " + WARNING_BODY,
    }
    missing_warning_lines = base_lines()
    missing_warning_lines[1:2] = [("Kentucky Straight", 48, True), ("Bourbon Whiskey", 48, False)]
    missing_warning_lines[5:7] = [(None, 64, False), (None, 250, False)]
    cases = [
        save_case("S01_clean_one", [panel(base_lines())], ref, ["one-panel", "clean", "warning-presentation", "proof-match", "applicability-above"]),
        save_case("S02_title_case", [panel(base_lines(warning_heading="Government Warning:"))], ref, ["capitalization", "warning"]),
        save_case("S03_abv_difference", [panel(base_lines(abv="40% Alc./Vol. (80 Proof)"))], ref, ["deterministic-mismatch", "abv", "proof"]),
        save_case("S04_missing_warning", [panel(missing_warning_lines)], ref, ["missing-warning", "applicability"]),
        save_case("S05_glare_blur", [panel(base_lines(), glare=True, blur=1.4)], ref, ["degradation", "glare", "blur"]),
    ]
    decoy = [("LIMITED EDITION 45% BARREL SERIES", 34, False)] + base_lines(abv="40% Alc./Vol. (80 Proof)")
    cases.append(save_case("S06_decoy_abv", [panel(decoy)], ref, ["decoy", "reference-blind"]))
    multi_lines = base_lines()
    multi_lines[1] = (multi_lines[1][0], 56, multi_lines[1][2])
    cases.append(save_case("S07_three_panel", [panel(multi_lines[:2]), panel(multi_lines[2:4]), panel(multi_lines[4:])], ref, ["three-panel", "split-fields"]))
    split = [[x] for x in multi_lines[:4]] + [[multi_lines[4], multi_lines[5]], [multi_lines[6], multi_lines[7]]]
    cases.append(save_case("S08_six_panel", [panel(x) for x in split], ref, ["six-panel", "split-fields", "warning-presentation"]))
    high_lines = [(text, int(size * 2.0), bold) for text, size, bold in base_lines()]
    cases.append(save_case("S09_high_resolution", [panel(high_lines, size=(3000, 4000))], ref, ["twelve-megapixel", "boundary", "safe-ocr-uncertainty"]))
    import_ref, import_lines = dict(ref), base_lines() + [("PRODUCT OF CANADA", 36, True)]
    import_ref["country"] = "CANADA"
    cases.append(save_case("S10_import_origin", [panel(import_lines)], import_ref, ["conditional-origin", "country-evidence"]))
    cases.append(save_case("S11_producer_difference", [panel(base_lines(producer="DIFFERENT HERITAGE DISTILLERY, LLC"))], ref, ["producer", "deterministic-mismatch"]))
    cases.append(save_case("S12_warning_typography", [panel(base_lines(heading_bold=False, body_bold=True))], ref, ["warning-presentation", "regular-heading-bold-body"]))
    cases.append(save_case("S13_warning_uncertain", [panel(base_lines(), text_fill="#b8b5ad", blur=0.8)], ref, ["warning-presentation", "low-contrast"]))
    brand_ref = dict(ref)
    brand_ref["brand"] = "Stone's Throw"
    cases.append(save_case("S14_brand_case", [panel(base_lines(brand="STONE'S THROW"))], brand_ref, ["brand", "case-only", "punctuation-preserved"]))
    cases.append(save_case("S15_proof_difference", [panel(base_lines(abv="45% Alc./Vol. (80 Proof)"))], ref, ["proof", "mismatch", "abv-proof-relationship"]))
    cases.append(save_case("S16_proof_missing", [panel(base_lines(abv="45% Alc./Vol."))], ref, ["proof", "missing"] ))
    cases.append(save_case("S17_proof_ambiguous", [panel(base_lines(abv="45% Alc./Vol. (90 Proof) ALSO 80 Proof"))], ref, ["proof", "ambiguous"] ))
    below_ref = dict(ref)
    below_ref.update({"abv": "0.4%", "proof": "0.8"})
    below_lines = base_lines(abv="0.4% Alc./Vol. (0.8 Proof)")
    below_lines[1:2] = [("Kentucky Straight", 48, True), ("Bourbon Whiskey", 48, False)]
    below_lines[5:7] = [(None, 64, False), (None, 250, False)]
    cases.append(save_case("S18_applicability_below", [panel(below_lines)], below_ref, ["warning-applicability", "below-threshold"] ))
    threshold_ref = dict(ref)
    threshold_ref.update({"abv": "0.5%", "proof": "1"})
    cases.append(save_case("S19_applicability_threshold", [panel(base_lines(abv="0.5% Alc./Vol. (1 Proof)"))], threshold_ref, ["warning-applicability", "at-threshold"] ))
    cases.append(save_case("S20_applicability_unparseable", [panel(base_lines(abv="Alcohol level unavailable (90 Proof)"))], ref, ["warning-applicability", "unparseable"] ))
    cases.append(save_case("S21_warning_missing_colon", [panel(base_lines(warning_heading="GOVERNMENT WARNING"))], ref, ["warning", "missing-colon"] ))
    cases.append(save_case("S22_warning_altered_heading", [panel(base_lines(warning_heading="GOVERNMENT WARNING: IMPORTANT"))], ref, ["warning", "altered-heading"] ))
    cases.append(save_case("S23_warning_bold_body", [panel(base_lines(heading_bold=True, body_bold=True))], ref, ["warning-presentation", "bold-heading-bold-body"] ))
    cases.append(save_case("S24_warning_regular_heading", [panel(base_lines(heading_bold=False, body_bold=False))], ref, ["warning-presentation", "regular-heading-regular-body"] ))
    punctuation_ref = dict(ref)
    punctuation_ref["producer"] = "OLD HERITAGE DISTILLERY LLC FRANKFORT KENTUCKY 40601"
    cases.append(save_case("S25_producer_punctuation", [panel(base_lines())], punctuation_ref, ["producer", "punctuation-only"] ))
    cases.append(save_case("S26_producer_missing", [panel(base_lines()[:6])], ref, ["producer", "missing"] ))
    producer_case_ref = dict(ref)
    producer_case_ref["producer"] = "Old Heritage Distillery, LLC Frankfort, Kentucky 40601"
    cases.append(save_case("S27_producer_case", [panel(base_lines())], producer_case_ref, ["producer", "case-only"] ))
    cases.append(save_case("S28_warning_heading_extra_period", [panel(base_lines(warning_heading="GOVERNMENT WARNING:."))], ref, ["warning", "punctuation", "extra-period"] ))
    body_added_period = WARNING_BODY.replace("should not drink alcoholic", "should not drink. alcoholic")
    cases.append(save_case("S29_warning_body_added_period", [panel(base_lines(warning_body=body_added_period))], ref, ["warning", "punctuation", "body-added-period"] ))
    body_duplicate_period = WARNING_BODY.replace("birth defects.", "birth defects..")
    cases.append(save_case("S30_warning_body_duplicate_punctuation", [panel(base_lines(warning_body=body_duplicate_period))], ref, ["warning", "punctuation", "duplicate-period"] ))
    low_evidence_body = WARNING_BODY.replace("health problems.", "health problems..")
    low_evidence_lines = base_lines(warning_body=low_evidence_body)
    cases.append(save_case("S31_warning_punctuation_uncertain", [panel(low_evidence_lines, text_fill="#b8b5ad", blur=0.8)], ref, ["warning", "punctuation", "low-evidence"] ))
    duplicate_country_panel = panel([("PRODUCT OF CANADA", 52, True), ("PRODUCT OF CANADA", 52, True)], size=(1200, 500))
    cases.append(save_case("S32_country_duplicate_same", [panel(base_lines()), duplicate_country_panel], import_ref, ["country", "duplicate-same"] ))
    conflicting_country_panel = panel([("PRODUCT OF CANADA", 52, True), ("PRODUCT OF USA", 52, True)], size=(1200, 500))
    cases.append(save_case("S33_country_conflicting", [panel(base_lines()), conflicting_country_panel], import_ref, ["country", "conflicting-candidates"] ))
    cases.append(save_case("S34_country_missing", [panel(base_lines())], import_ref, ["country", "missing"] ))
    unreadable_origin = panel([("PRODUCT OF CANADA", 36, True)], text_fill="#eeeeee", blur=2.5)
    cases.append(save_case("S35_country_unreadable", [panel(base_lines()), unreadable_origin], import_ref, ["country", "unreadable", "two-panel"] ))
    decoy_country_lines = [("RECIPE INSPIRED BY USA", 34, False)] + base_lines() + [("PRODUCT OF CANADA", 36, True)]
    cases.append(save_case("S36_country_decoy", [panel(decoy_country_lines)], import_ref, ["country", "decoy", "reference-blind"] ))
    mismatch_country_lines = base_lines() + [("PRODUCT OF USA", 36, True)]
    cases.append(save_case("S37_country_mismatch", [panel(mismatch_country_lines)], import_ref, ["country", "mismatch"] ))
    return cases


def case_paths(case):
    return [str((ROOT / path).resolve()) for path in case["paths"]]


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def contact_sheet(paths):
    decoded_pixels, cell_w, cell_h = 0, 900, 1100
    cols = 1 if len(paths) == 1 else (2 if len(paths) <= 4 else 3)
    rows = math.ceil(len(paths) / cols)
    canvas = Image.new("RGB", (cols * cell_w, rows * cell_h), "white")
    panel_boxes = []
    for index, path in enumerate(paths):
        with Image.open(path) as source:
            source.load()
            decoded_pixels += source.width * source.height
            source = ImageEnhance.Contrast(source.convert("RGB")).enhance(1.05)
            source.thumbnail((cell_w - 20, cell_h - 20), Image.Resampling.LANCZOS)
            x = (index % cols) * cell_w + (cell_w - source.width) // 2
            y = (index // cols) * cell_h + (cell_h - source.height) // 2
            canvas.paste(source, (x, y))
            panel_boxes.append([index + 1, x, y, x + source.width, y + source.height])
    return canvas, panel_boxes, decoded_pixels


def panel_for_box(box, panel_boxes):
    xs, ys = [p[0] for p in box], [p[1] for p in box]
    cx, cy = sum(xs) / len(xs), sum(ys) / len(ys)
    return next((number for number, left, top, right, bottom in panel_boxes if left <= cx <= right and top <= cy <= bottom), None)


def raster_metrics(image_array, box):
    xs, ys = [p[0] for p in box], [p[1] for p in box]
    left, right = max(0, int(min(xs)) - 2), min(image_array.shape[1], int(max(xs)) + 3)
    top, bottom = max(0, int(min(ys)) - 2), min(image_array.shape[0], int(max(ys)) + 3)
    crop = image_array[top:bottom, left:right]
    if crop.size == 0:
        return {"contrast": 0.0, "stroke_ratio": 0.0, "ink_density": 0.0, "height": 0.0}
    gray = cv2.cvtColor(crop, cv2.COLOR_RGB2GRAY)
    contrast = float(np.percentile(gray, 95) - np.percentile(gray, 5))
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    distance = cv2.distanceTransform(binary, cv2.DIST_L2, 3)
    foreground, height = distance[distance > 0], max(1.0, max(ys) - min(ys))
    stroke_ratio = float(np.percentile(foreground, 75) / height) if foreground.size else 0.0
    ink_density = float(np.mean(binary > 0))
    return {
        "contrast": round(contrast, 3),
        "stroke_ratio": round(stroke_ratio, 6),
        "ink_density": round(ink_density, 6),
        "height": round(height, 3),
    }


def observed_candidates(items, panel_boxes, sheet):
    image_array, records = np.asarray(sheet.convert("RGB")), []
    for item in items:
        if item["score"] < 0.50:
            continue
        box = item["box"]
        records.append({
            "text": normalize_text(item["txt"]), "score": round(float(item["score"]), 6), "box": box,
            "panel": panel_for_box(box, panel_boxes), "top": min(p[1] for p in box), "left": min(p[0] for p in box),
            "bottom": max(p[1] for p in box), "metrics": raster_metrics(image_array, box),
        })
    records.sort(key=lambda r: (r["panel"] or 999, r["top"], r["left"]))
    lines = [r["text"] for r in records]
    abv_candidates, proof_candidates, net_candidates, country_candidates = [], [], [], []
    for record in records:
        line = record["text"]
        if "ALC" in line.upper() or "PROOF" in line.upper():
            for match in re.finditer(r"(?<!\d)(\d{1,2}(?:\.\d+)?)\s*%", line):
                abv_candidates.append({"value": float(match.group(1)), "record": record})
            for match in re.finditer(r"(?<!\d)(\d{1,3}(?:\.\d+)?)\s*PROOF", line, re.IGNORECASE):
                proof_candidates.append({"value": float(match.group(1)), "record": record})
        for match in re.finditer(r"(?<!\d)(\d{2,4})\s*M[LlI1]", line, re.IGNORECASE):
            net_candidates.append({"value": int(match.group(1)), "record": record})
        compact = re.sub(r"[^A-Z]", "", line.upper())
        origin_match = re.search(r"PRODUCTOF([A-Z]+)", compact)
        if origin_match:
            country_candidates.append({"value": origin_match.group(1), "record": record})
    warning_index = next((i for i, r in enumerate(records) if "WARNING" in r["text"].upper()), None)
    heading = records[warning_index] if warning_index is not None else None
    producer_index = next((i for i, r in enumerate(records) if "BOTTLED" in r["text"].upper()), None)
    body = []
    if warning_index is not None:
        end = producer_index if producer_index is not None and producer_index > warning_index else len(records)
        body = [r for r in records[warning_index + 1:end] if r["panel"] == heading["panel"]]
    parts = [record["text"].strip() for record in body]
    excluded = ("WARNING", "BOURBON", "WHISKEY", "ALC", "PROOF", "BOTTLED", "PRODUCT OF")
    brand_rows = [(r["metrics"]["height"], r) for r in records if not any(t in r["text"].upper() for t in excluded) and not re.search(r"\d", r["text"])]
    brand_rows.sort(key=lambda pair: pair[0], reverse=True)
    class_record = next((r for r in records if "BOURBON" in r["text"].upper() and "WHISKEY" in r["text"].upper()), None)
    if class_record is not None:
        class_index = records.index(class_record)
        preceding = records[class_index - 1] if class_index > 0 else None
        if preceding and preceding["panel"] == class_record["panel"] and any(token in preceding["text"].upper() for token in ("KENTUCKY", "STRAIGHT")):
            left = min(preceding["left"], class_record["left"])
            right = max(max(point[0] for point in preceding["box"]), max(point[0] for point in class_record["box"]))
            top = min(preceding["top"], class_record["top"])
            bottom = max(preceding["bottom"], class_record["bottom"])
            class_record = {
                **class_record,
                "text": normalize_text(f"{preceding['text']} {class_record['text']}"),
                "box": [[left, top], [right, top], [right, bottom], [left, bottom]],
                "top": top,
                "bottom": bottom,
            }
    if class_record is None:
        for index, record in enumerate(records[:-1]):
            following = records[index + 1]
            if "BOURBON" in record["text"].upper() and "WHISKEY" in following["text"].upper() and record["panel"] == following["panel"]:
                left = min(record["left"], following["left"])
                right = max(max(point[0] for point in record["box"]), max(point[0] for point in following["box"]))
                top = min(record["top"], following["top"])
                bottom = max(record["bottom"], following["bottom"])
                class_record = {
                    **record,
                    "text": normalize_text(f"{record['text']} {following['text']}"),
                    "box": [[left, top], [right, top], [right, bottom], [left, bottom]],
                    "top": top,
                    "bottom": bottom,
                }
                break
    producer_records = []
    if producer_index is not None:
        producer_panel = records[producer_index]["panel"]
        for record in records[producer_index:]:
            if record["panel"] != producer_panel or "PRODUCT OF" in record["text"].upper():
                break
            producer_records.append(record)
    producer_parts = []
    for index, record in enumerate(producer_records):
        value = record["text"]
        if index == 0:
            value = re.sub(r"^.*?BOTTLED\s*BY\s*:?\s*", "", value, flags=re.IGNORECASE)
        producer_parts.append(value)
    return {
        "records": records, "lines": lines, "brand_candidate": brand_rows[0][1] if brand_rows else None,
        "class_candidate": class_record, "abv_candidates": abv_candidates, "proof_candidates": proof_candidates,
        "net_candidates": net_candidates,
        "warning_heading_record": heading, "warning_body_records": body, "warning_body": normalize_text(" ".join(parts)),
        "producer_candidate": normalize_text(" ".join(producer_parts)) or None, "producer_records": producer_records,
        "country_candidates": country_candidates,
    }


def confirm_warning_boundary_punctuation(ocr, sheet, observed):
    checks = []
    body = observed["warning_body_records"]
    for index, record in enumerate(body[:-1]):
        if not (record["text"].endswith(".") and body[index + 1]["text"][:1].islower()):
            continue
        xs = [point[0] for point in record["box"]]
        ys = [point[1] for point in record["box"]]
        crop = sheet.crop((max(0, min(xs) - 3), max(0, min(ys) - 3), min(sheet.width, max(xs) + 3), min(sheet.height, max(ys) + 3)))
        secondary = ocr(crop, use_det=False, use_cls=False, use_rec=True, text_score=0.25)
        secondary_text = normalize_text(" ".join(secondary.txts or ()))
        checks.append({
            "body_record_index": index,
            "primary_text": record["text"],
            "secondary_text": secondary_text,
            "secondary_score": round(float(np.median(secondary.scores)), 6) if secondary.scores else 0.0,
            "punctuation_confirmed": secondary_text.endswith("."),
            "evidence_ref": evidence(record),
        })
    observed["warning_boundary_punctuation_checks"] = checks
    uncertain_indexes = {
        item["body_record_index"]
        for item in checks
        if not item["punctuation_confirmed"]
    }
    uncertainty_parts = []
    for index, record in enumerate(body):
        value = record["text"]
        if index in uncertain_indexes and value.endswith("."):
            value = value[:-1]
        uncertainty_parts.append(value)
    observed["warning_body_after_uncertain_boundary_removal"] = normalize_text(" ".join(uncertainty_parts))


def quality_review(paths):
    scores = []
    for path in paths:
        image = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            return True, [{"path": Path(path).name, "reason": "decode failed"}]
        score = float(cv2.Laplacian(image, cv2.CV_64F).var())
        scores.append({"path": Path(path).name, "laplacian_variance": round(score, 2)})
    return any(item.get("laplacian_variance", 0) < 100.0 for item in scores), scores


def evidence(record):
    return {"panel": record["panel"], "polygon": record["box"]} if record else None


def field(check_id, reference_display, extracted_display, state, reason_code, reason_text, evidence_ref, capability="Automated selected check", applicable=True, alternatives=None):
    result = {
        "check_id": check_id, "reference_display": reference_display, "extracted_display": extracted_display,
        "state": state, "reason_code": reason_code, "reason_text": reason_text, "evidence_ref": evidence_ref,
        "policy_id": f"{check_id}-policy", "policy_version": "baird-spike-v3", "capability": capability,
        "applicable": applicable, "alternatives": alternatives or [],
    }
    return result


def exact_case_punctuation_state(observed, expected):
    if not observed:
        return "Not verified", "candidate_missing", "No independently located candidate was readable"
    observed_ws, expected_ws = normalize_text(observed), normalize_text(expected)
    if observed_ws == expected_ws:
        return "Match", "exact_match", "Exact observed value matches the reference"
    if observed_ws.casefold() == expected_ws.casefold():
        return "Review", "case_difference", "The same characters use different capitalization"
    if re.sub(r"[^a-z0-9]", "", observed_ws.casefold()) == re.sub(r"[^a-z0-9]", "", expected_ws.casefold()):
        return "Review", "punctuation_difference", "The same letters and numbers use different punctuation"
    return "Mismatch", "observed_value_differs", "The independently located observed value differs"


def warning_presentation(observed, quality_is_review, warning_checks_applicable=True):
    heading, body = observed["warning_heading_record"], observed["warning_body_records"]
    presentation_rows = (
        ("warning_heading_emphasis", "Heading emphasized relative to body"),
        ("warning_body_not_bold", "Remaining warning text not bold"),
        ("warning_separation", "Warning separate and apart"),
        ("warning_continuity", "Warning statement continuous"),
        ("warning_contrast_legibility", "Warning contrast and legibility"),
    )
    if not warning_checks_applicable:
        return [
            field(check_id, reference, None, "Not verified", "warning_not_applicable", "The warning is not required below 0.5 percent ABV", None, "Active with evidence limit", applicable=False)
            for check_id, reference in presentation_rows
        ]
    if not heading:
        return [
            field(check_id, reference, None, "Not verified", "warning_not_found", "The required warning region was not found", None, "Active with evidence limit")
            for check_id, reference in presentation_rows
        ]
    body_metrics = [r["metrics"] for r in body if r["metrics"]["ink_density"] > 0]
    body_stroke = float(np.median([m["stroke_ratio"] for m in body_metrics])) if body_metrics else 0.0
    body_density = float(np.median([m["ink_density"] for m in body_metrics])) if body_metrics else 0.0
    heading_stroke = heading["metrics"]["stroke_ratio"]
    heading_density = heading["metrics"]["ink_density"]
    ratio = heading_stroke / body_stroke if body_stroke else 0.0
    if not body_metrics or quality_is_review:
        emphasis_state = body_weight_state = "Review"
        emphasis_code = body_weight_code = "image_quality_insufficient"
        emphasis_reason = body_weight_reason = "Image evidence is insufficient for a reliable weight decision"
    else:
        comparable_heading = heading["text"] == "GOVERNMENT WARNING:"
        if not comparable_heading:
            emphasis_state, emphasis_code = "Review", "heading_emphasis_not_comparable"
            emphasis_reason = "Heading glyphs differ from the calibrated uppercase sample, so emphasis remains for review"
        elif ratio >= 1.50:
            emphasis_state, emphasis_code = "Match", "heading_emphasis_match"
            emphasis_reason = f"Independent heading density and relative stroke evidence support emphasis, density {heading_density:.3f}, ratio {ratio:.3f}"
        elif ratio <= 1.45:
            emphasis_state, emphasis_code = "Mismatch", "heading_emphasis_difference"
            emphasis_reason = f"Independent heading density or relative stroke evidence fails emphasis, density {heading_density:.3f}, ratio {ratio:.3f}"
        else:
            emphasis_state, emphasis_code = "Review", "heading_emphasis_uncertain"
            emphasis_reason = f"Heading emphasis evidence is inconclusive, density {heading_density:.3f}, ratio {ratio:.3f}"
        if body_density <= 0.165:
            body_weight_state, body_weight_code = "Match", "body_regular_match"
            body_weight_reason = f"Independent body-glyph density supports regular weight, density {body_density:.3f}"
        elif body_density >= 0.17:
            body_weight_state, body_weight_code = "Mismatch", "body_weight_difference"
            body_weight_reason = f"Independent body-glyph density supports prohibited bold treatment, density {body_density:.3f}"
        else:
            body_weight_state, body_weight_code = "Review", "body_weight_uncertain"
            body_weight_reason = f"Body weight evidence is inconclusive, density {body_density:.3f}"
    same_panel = [r for r in observed["records"] if r["panel"] == heading["panel"]]
    warning_ids = {id(heading), *[id(r) for r in body]}
    unrelated = [r for r in same_panel if id(r) not in warning_ids and not r["bottom"] < heading["top"]]
    producer = observed["producer_records"][0] if observed["producer_records"] else None
    if quality_is_review:
        separation_state, separation_reason = "Review", "Image quality does not support a separation decision"
        separation_code = "image_quality_insufficient"
    elif producer and producer["panel"] == heading["panel"] and body:
        body_height = float(np.median([r["metrics"]["height"] for r in body]))
        gap_ratio = (producer["top"] - max(r["bottom"] for r in body)) / max(body_height, 1.0)
        if gap_ratio >= 0.10:
            separation_state, separation_reason = "Match", f"Visible boundary separates warning and producer text, gap ratio {gap_ratio:.3f}"
            separation_code = "layout_separation"
        else:
            separation_state, separation_reason = "Review", f"Separation boundary is inconclusive, gap ratio {gap_ratio:.3f}"
            separation_code = "layout_separation"
    elif not unrelated:
        separation_state, separation_reason = "Match", "Warning occupies a separate supplied panel region"
        separation_code = "layout_separation"
    else:
        separation_state, separation_reason = "Review", "Neighboring same-panel text makes separation uncertain"
        separation_code = "layout_separation"
    canonical_tokens = set(re.findall(r"[a-z]+", WARNING_BODY.casefold()))
    interruption = any((lambda tokens: tokens and len(tokens & canonical_tokens) / len(tokens) < 0.50)(set(re.findall(r"[a-z]+", r["text"].casefold()))) for r in body)
    if quality_is_review or not body:
        continuity_state = "Review" if body else "Not verified"
        continuity_reason = "Image evidence is insufficient for a continuity decision"
        continuity_code = "image_quality_insufficient" if quality_is_review else "layout_continuity"
    elif interruption:
        continuity_state, continuity_reason = "Mismatch", "Non-warning material interrupts the observed warning block"
        continuity_code = "layout_continuity"
    else:
        continuity_state, continuity_reason = "Match", "Observed warning lines form one uninterrupted block"
        continuity_code = "layout_continuity"
    warning_records = [heading] + body
    median_score = float(np.median([r["score"] for r in warning_records]))
    contrast = float(np.median([r["metrics"]["contrast"] for r in warning_records]))
    if not quality_is_review and median_score >= 0.82 and contrast >= 110:
        contrast_state, contrast_reason = "Match", f"OCR agreement and local contrast meet the evidence floor, score {median_score:.3f}, contrast {contrast:.1f}"
        contrast_code = "contrast_legibility"
    elif median_score >= 0.82 and contrast < 45:
        contrast_state, contrast_reason = "Mismatch", f"Observed warning contrast is clearly below the calibrated floor, contrast {contrast:.1f}"
        contrast_code = "contrast_legibility"
    else:
        contrast_state, contrast_reason = "Review", f"Contrast or OCR agreement is insufficient, score {median_score:.3f}, contrast {contrast:.1f}"
        contrast_code = "image_quality_insufficient" if quality_is_review else "contrast_legibility"
    return [
        field("warning_heading_emphasis", "Heading emphasized relative to body", f"heading density {heading_density:.3f}; stroke ratio {ratio:.3f}", emphasis_state, emphasis_code, emphasis_reason, evidence(heading), "Active with evidence limit"),
        field("warning_body_not_bold", "Remaining warning text not bold", f"body density {body_density:.3f}", body_weight_state, body_weight_code, body_weight_reason, evidence(body[0]) if body else None, "Active with evidence limit"),
        field("warning_separation", "Warning separate and apart", "layout boundary evaluated", separation_state, separation_code, separation_reason, evidence(heading), "Active with evidence limit"),
        field("warning_continuity", "Warning statement continuous", "reading order evaluated", continuity_state, continuity_code, continuity_reason, evidence(heading), "Active with evidence limit"),
        field("warning_contrast_legibility", "Warning contrast and legibility", f"score {median_score:.3f}; contrast {contrast:.1f}", contrast_state, contrast_code, contrast_reason, evidence(heading), "Active with evidence limit"),
    ]


def compare(observed, reference, panel_count):
    fields = []
    brand_record = observed["brand_candidate"]
    brand_text = brand_record["text"] if brand_record else None
    state, code, reason = exact_case_punctuation_state(brand_text, reference["brand"])
    fields.append(field("brand", reference["brand"], brand_text, state, code, reason, evidence(brand_record)))

    class_record = observed["class_candidate"]
    class_text = class_record["text"] if class_record else None
    state, code, reason = exact_case_punctuation_state(class_text, reference["class_type"])
    fields.append(field("class_type", reference["class_type"], class_text, state, code, reason, evidence(class_record)))

    abvs = observed["abv_candidates"]
    unique_abvs = sorted({item["value"] for item in abvs})
    observed_abv = unique_abvs[0] if len(unique_abvs) == 1 else None
    if not abvs:
        fields.append(field("abv", reference["abv"], None, "Not verified", "abv_missing", "No anchored percent candidate was found", None))
    elif len(unique_abvs) > 1:
        fields.append(field("abv", reference["abv"], ", ".join(f"{value:g}%" for value in unique_abvs), "Review", "abv_ambiguous", "Multiple independently plausible ABV candidates remain", evidence(abvs[0]["record"])))
    elif observed_abv == float(reference["abv"].rstrip("%")):
        fields.append(field("abv", reference["abv"], f"{observed_abv:g}%", "Match", "numeric_match", "The single anchored ABV candidate matches", evidence(abvs[0]["record"])))
    else:
        fields.append(field("abv", reference["abv"], f"{observed_abv:g}%", "Mismatch", "numeric_difference", "The single anchored ABV candidate differs", evidence(abvs[0]["record"])))

    proofs = observed["proof_candidates"]
    unique_proofs = sorted({item["value"] for item in proofs})
    proof_applicable = reference.get("proof") is not None or bool(proofs)
    expected_proof = float(reference["proof"]) if reference.get("proof") is not None else None
    if not proof_applicable:
        fields.append(field("proof", "Not provided", None, "Not verified", "proof_not_applicable", "Neither the reference nor label presents proof", None, applicable=False))
    elif not proofs:
        fields.append(field("proof", reference.get("proof"), None, "Not verified", "proof_missing", "The reference presents proof but no label proof candidate was found", None))
    elif len(unique_proofs) > 1:
        fields.append(field("proof", reference.get("proof"), ", ".join(f"{value:g}" for value in unique_proofs), "Review", "proof_ambiguous", "Multiple independently plausible proof candidates remain", evidence(proofs[0]["record"])))
    else:
        observed_proof = unique_proofs[0]
        relationship_ok = observed_abv is not None and abs(observed_proof - 2 * observed_abv) < 0.001
        reference_ok = expected_proof is None or abs(observed_proof - expected_proof) < 0.001
        if relationship_ok and reference_ok:
            fields.append(field("proof", reference.get("proof"), f"{observed_proof:g}", "Match", "proof_match", "Observed proof matches the reference and the two-times-ABV relationship", evidence(proofs[0]["record"])))
        elif observed_abv is None and reference_ok:
            fields.append(field("proof", reference.get("proof"), f"{observed_proof:g}", "Review", "proof_relationship_uncertain", "Observed proof matches the reference, but ABV evidence is insufficient to verify the relationship", evidence(proofs[0]["record"])))
        else:
            fields.append(field("proof", reference.get("proof"), f"{observed_proof:g}", "Mismatch", "proof_difference", "Observed proof differs from the reference or the two-times-ABV relationship", evidence(proofs[0]["record"])))

    nets, expected_net = observed["net_candidates"], int(re.search(r"\d+", reference["net_contents"]).group())
    unique_nets = sorted({item["value"] for item in nets})
    if not nets:
        fields.append(field("net_contents", reference["net_contents"], None, "Not verified", "volume_missing", "No anchored volume candidate was found", None))
    elif len(unique_nets) > 1:
        fields.append(field("net_contents", reference["net_contents"], ", ".join(str(value) for value in unique_nets), "Review", "volume_ambiguous", "Multiple independently plausible volume candidates remain", evidence(nets[0]["record"])))
    elif unique_nets[0] == expected_net:
        fields.append(field("net_contents", reference["net_contents"], f"{unique_nets[0]} mL", "Match", "volume_match", "The single anchored volume candidate matches", evidence(nets[0]["record"])))
    else:
        fields.append(field("net_contents", reference["net_contents"], f"{unique_nets[0]} mL", "Mismatch", "volume_difference", "The single anchored volume candidate differs", evidence(nets[0]["record"])))

    producer = observed["producer_candidate"]
    state, code, reason = exact_case_punctuation_state(producer, reference["producer"])
    fields.append(field("producer", reference["producer"], producer, state, code, reason, evidence(observed["producer_records"][0]) if observed["producer_records"] else None))

    countries = observed["country_candidates"]
    unique_country_values = sorted({item["value"] for item in countries})
    if not reference.get("country"):
        fields.append(field("country", "Domestic reference", None, "Not verified", "country_not_applicable", "Country of origin is conditional and this reference is domestic", None, applicable=False))
    elif not countries:
        fields.append(field("country", reference["country"], None, "Not verified", "country_missing", "The required import origin was not found", None))
    elif len(unique_country_values) > 1:
        alternatives = []
        for value in unique_country_values:
            candidate = next(item for item in countries if item["value"] == value)
            alternatives.append({"value": value, "evidence_ref": evidence(candidate["record"])})
        fields.append(field(
            "country", reference["country"], ", ".join(unique_country_values), "Review", "country_ambiguous",
            "Multiple independently plausible country-of-origin candidates remain",
            alternatives[0]["evidence_ref"], alternatives=alternatives,
        ))
    elif unique_country_values[0] == reference["country"]:
        fields.append(field("country", reference["country"], countries[0]["value"], "Match", "country_match", "The observed import origin matches", evidence(countries[0]["record"])))
    else:
        fields.append(field("country", reference["country"], countries[0]["value"], "Mismatch", "country_difference", "The observed import origin differs", evidence(countries[0]["record"])))

    heading = observed["warning_heading_record"]
    heading_text = heading["text"] if heading else None
    warning_text = observed["warning_body"]
    warning_present = bool(heading and warning_text)
    warning_required = None if observed_abv is None else observed_abv >= WARNING_THRESHOLD
    applicability_evidence = evidence(abvs[0]["record"]) if abvs else None
    if warning_required is None:
        fields.append(field("warning_applicability", "Required at or above 0.5 percent ABV", None, "Review", "warning_applicability_uncertain", "ABV evidence is insufficient to establish warning applicability", applicability_evidence))
    elif warning_required and warning_present:
        fields.append(field("warning_applicability", "Required at or above 0.5 percent ABV", "Warning required and located", "Match", "warning_required_present", "Observed ABV requires the warning and the warning region is present", applicability_evidence))
    elif warning_required:
        fields.append(field("warning_applicability", "Required at or above 0.5 percent ABV", "Warning required but not located", "Mismatch", "warning_required_missing", "Observed ABV requires the warning, but no complete warning region was located", applicability_evidence))
    else:
        fields.append(field("warning_applicability", "Required at or above 0.5 percent ABV", "Warning not required", "Match", "warning_not_required", "Observed ABV is below 0.5 percent", applicability_evidence))

    warning_checks_applicable = warning_required is not False
    if not warning_checks_applicable:
        fields.append(field("warning_heading_uppercase", "GOVERNMENT WARNING:", None, "Not verified", "warning_not_applicable", "The warning is not required below 0.5 percent ABV", None, applicable=False))
        fields.append(field("warning_wording", WARNING_BODY, None, "Not verified", "warning_not_applicable", "The warning is not required below 0.5 percent ABV", None, applicable=False))
    else:
        if not heading_text:
            h_state, h_code, h_reason = "Not verified", "warning_heading_missing", "The warning heading was not found"
        elif heading_text == WARNING_HEADING:
            h_state, h_code, h_reason = "Match", "warning_heading_exact", "The exact uppercase heading and colon were observed"
        elif heading_text.casefold() == WARNING_HEADING.casefold():
            h_state, h_code, h_reason = "Mismatch", "warning_heading_case", "The heading capitalization differs"
        elif heading_text == WARNING_HEADING.rstrip(":"):
            h_state, h_code, h_reason = "Mismatch", "warning_heading_punctuation", "The required colon is missing"
        else:
            h_state, h_code, h_reason = "Mismatch", "warning_heading_altered", "Readable heading text contains added or altered characters"
        fields.append(field("warning_heading_uppercase", "GOVERNMENT WARNING:", heading_text, h_state, h_code, h_reason, evidence(heading)))
        if not warning_text:
            w_state, w_code, w_reason = "Not verified", "warning_wording_missing", "The prescribed warning body was not found"
        elif normalize_text(warning_text) == normalize_text(WARNING_BODY):
            w_state, w_code, w_reason = "Match", "warning_wording_exact", "The prescribed wording matches after whitespace and line-wrap normalization"
        else:
            score = float(np.median([record["score"] for record in observed["warning_body_records"]])) if observed["warning_body_records"] else 0.0
            definite_difference_remains = (
                observed.get("warning_body_after_uncertain_boundary_removal", warning_text)
                != normalize_text(WARNING_BODY)
            )
            if score >= 0.82 and not observed["quality_review"] and definite_difference_remains:
                w_state, w_code, w_reason = "Mismatch", "warning_wording_difference", "Readable observed warning wording differs from prescribed text"
            else:
                w_state, w_code, w_reason = "Review", "warning_wording_uncertain", "OCR or secondary punctuation evidence is insufficient for a definite wording decision"
        fields.append(field("warning_wording", WARNING_BODY, warning_text or None, w_state, w_code, w_reason, evidence(observed["warning_body_records"][0]) if observed["warning_body_records"] else None))

    fields.extend(warning_presentation(observed, observed["quality_review"], warning_checks_applicable))

    required_checks = ["brand", "class_type", "abv", "net_contents", "producer"]
    if proof_applicable:
        required_checks.append("proof")
    if reference.get("country"):
        required_checks.append("country")
    if warning_checks_applicable:
        required_checks.extend(["warning_heading_uppercase", "warning_wording"])
    field_map = {item["check_id"]: item for item in fields}
    required_present = all(field_map[check]["state"] != "Not verified" for check in required_checks)
    fields.append(field("panel_coverage", "Required evidence across 1 to 6 supplied panels", f"{panel_count} panels decoded", "Match" if required_present else "Review", "panel_coverage", "All required field regions were evaluated" if required_present else "One or more required field regions were unavailable", None))

    if observed["quality_review"]:
        fields.append(field("image_quality", "Readable bounded image quality", "Blur or contrast floor not met", "Review", "image_quality_review", "At least one panel needs clearer evidence", None, "Quality gate"))
    else:
        fields.append(field("image_quality", "Readable bounded image quality", "Quality floor met", "Match", "image_quality_match", "All panels meet the bounded architecture-slice quality floor", None, "Quality gate"))

    emitted_ids = [item["check_id"] for item in fields]
    omitted = sorted(set(ALL_CHECK_IDS) - set(emitted_ids))
    duplicates = sorted({check_id for check_id in emitted_ids if emitted_ids.count(check_id) > 1})
    if omitted or duplicates:
        raise AssertionError(f"Registry mismatch, omitted={omitted}, duplicates={duplicates}")
    aggregating = [item for item in fields if item["applicable"]]
    states = [item["state"] for item in aggregating]
    summary = "Differences detected" if "Mismatch" in states else ("Review needed" if "Review" in states or "Not verified" in states else "No differences found in checked fields")
    if summary == "No differences found in checked fields":
        non_match = [item["check_id"] for item in aggregating if item["state"] != "Match"]
        if non_match:
            raise AssertionError(f"False clean from non-Match checks: {non_match}")
    return {
        "request_id": "spike-request", "app_version": "baird-spike-v3", "profile_id": "selected-distilled-spirits",
        "profile_version": "baird-v1", "rule_sources": ["27 CFR Part 16", "27 CFR 5.63"],
        "registry_id": CHECK_REGISTRY["registry_id"], "registry_version": CHECK_REGISTRY["registry_version"],
        "panels": {"count": panel_count, "quality_scores": observed["quality_scores"]}, "fields": fields,
        "human_only_limitations": ["Physical warning type size is not automatically assessed without reliable scale evidence"],
        "summary": summary, "limitations": ["Synthetic architecture-feasibility evidence, not production accuracy evidence"],
    }


def expected_fields(case_id):
    expected = {check_id: dict(value) for check_id, value in EXPECTED_MANIFEST["base_fields"].items()}
    for check_id, override in EXPECTED_MANIFEST["cases"][case_id]["overrides"].items():
        expected[check_id].update(override)
    return expected


def validate_against_oracle(case_id, result):
    expected = expected_fields(case_id)
    actual = {item["check_id"]: item for item in result["fields"]}
    errors = []
    if set(expected) != set(ALL_CHECK_IDS):
        errors.append("Oracle registry does not equal selected-check registry")
    if set(actual) != set(ALL_CHECK_IDS):
        errors.append("Result registry does not equal selected-check registry")
    for check_id in ALL_CHECK_IDS:
        if check_id not in expected or check_id not in actual:
            continue
        wanted, got = expected[check_id], actual[check_id]
        for key in ("applicable", "state", "reason_code"):
            if got.get(key) != wanted[key]:
                errors.append(f"{check_id}.{key}: expected {wanted[key]!r}, got {got.get(key)!r}")
        if wanted["evidence_required"] and not got.get("evidence_ref"):
            errors.append(f"{check_id}.evidence_ref: required evidence is missing")
        if "expected_alternatives" in wanted:
            alternatives = got.get("alternatives")
            values = [item.get("value") for item in alternatives] if isinstance(alternatives, list) else None
            if values != wanted["expected_alternatives"]:
                errors.append(f"{check_id}.alternatives: expected {wanted['expected_alternatives']!r}, got {values!r}")
            evidence_items = [item.get("evidence_ref") for item in alternatives] if isinstance(alternatives, list) else []
            if wanted.get("alternative_evidence_required") and any(not item for item in evidence_items):
                errors.append(f"{check_id}.alternatives.evidence_ref: every alternative requires evidence")
            if wanted.get("distinct_alternative_evidence"):
                polygons = [json.dumps(item.get("polygon"), sort_keys=True) for item in evidence_items if item]
                if len(polygons) != len(set(polygons)):
                    errors.append(f"{check_id}.alternatives.evidence_ref: alternative polygons must be distinct")
    expected_summary = EXPECTED_MANIFEST["cases"][case_id]["summary"]
    if result["summary"] != expected_summary:
        errors.append(f"summary: expected {expected_summary!r}, got {result['summary']!r}")
    return expected_summary, errors


class PeakSampler:
    def __init__(self):
        self.proc, self.stop = psutil.Process(), threading.Event()
        self.peak = self.proc.memory_info().rss
        self.thread = threading.Thread(target=self.run, daemon=True)
    def run(self):
        while not self.stop.wait(0.01):
            self.peak = max(self.peak, self.proc.memory_info().rss)
    def __enter__(self):
        self.thread.start()
        return self
    def __exit__(self, *args):
        self.stop.set(); self.thread.join(); self.peak = max(self.peak, self.proc.memory_info().rss)


def run_paths(ocr, paths, reference, case_id, expected_summary, iteration):
    t0 = time.perf_counter()
    total_bytes = sum(Path(path).stat().st_size for path in paths)
    sheet, panel_boxes, decoded_pixels = contact_sheet(paths)
    t1 = time.perf_counter()
    result = ocr(sheet, use_det=True, use_cls=True, use_rec=True, unclip_ratio=2.0, box_thresh=0.35, text_score=0.35)
    items = result.to_json() if result.boxes is not None else []
    observed = observed_candidates(items, panel_boxes, sheet)
    confirm_warning_boundary_punctuation(ocr, sheet, observed)
    t2 = time.perf_counter()
    observed["quality_review"], observed["quality_scores"] = quality_review(paths)
    compared = compare(observed, reference, len(paths))
    payload = {"case_id": case_id, "panel_boxes": panel_boxes, "result": compared}
    encoded = json.dumps(payload, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    json.loads(encoded)
    t3 = time.perf_counter()
    oracle_summary, validation_errors = (validate_against_oracle(case_id, compared) if case_id in EXPECTED_MANIFEST["cases"] else (expected_summary, []))
    expected_summary = oracle_summary or expected_summary
    return {
        "case_id": case_id, "iteration": iteration, "panel_count": len(paths), "input_bytes": total_bytes,
        "decoded_pixels": decoded_pixels, "working_pixels": sheet.width * sheet.height,
        "decode_preprocess_ms": round((t1 - t0) * 1000, 2), "ocr_ms": round((t2 - t1) * 1000, 2),
        "rules_serialize_ms": round((t3 - t2) * 1000, 2), "server_pipeline_ms": round((t3 - t0) * 1000, 2),
        "summary": compared["summary"], "expected_summary": expected_summary,
        "expected_correct": not validation_errors if expected_summary else None,
        "field_validation_errors": validation_errors,
        "field_mismatch_count": len(validation_errors),
        "missing_evidence_count": sum("evidence_ref" in error for error in validation_errors),
        "false_clean_count": int(compared["summary"] == "No differences found in checked fields" and any(item["applicable"] and item["state"] != "Match" for item in compared["fields"])),
        "false_mismatch_count": sum(
            1 for check_id, expected in expected_fields(case_id).items()
            if case_id in EXPECTED_MANIFEST["cases"] and expected["state"] != "Mismatch" and next(item for item in compared["fields"] if item["check_id"] == check_id)["state"] == "Mismatch"
        ) if case_id in EXPECTED_MANIFEST["cases"] else 0,
        "field_count": len(compared["fields"]),
        "active_check_count": sum(item["applicable"] for item in compared["fields"]), "ocr_lines": len(items),
        "response_bytes": len(encoded), "payload": payload,
    }


def percentile(values, q):
    ordered = sorted(values)
    return ordered[max(0, math.ceil(q * len(ordered)) - 1)]


def main():
    proc = psutil.Process()
    affinity_before = proc.cpu_affinity()
    proc.cpu_affinity(affinity_before[:2])
    cases = make_cases()
    (RESULTS / "fixture-manifest.json").write_text(json.dumps(cases, indent=2), encoding="utf-8")
    case_filter = os.environ.get("SPIKE_CASES")
    if case_filter:
        allowed = {item.strip() for item in case_filter.split(",") if item.strip()}
        cases = [case for case in cases if case["case_id"] in allowed]
    iterations = int(os.environ.get("SPIKE_ITERATIONS", "3"))
    init_start = time.perf_counter()
    with PeakSampler() as init_peak:
        ocr = RapidOCR(params=ocr_params())
    init_ms = (time.perf_counter() - init_start) * 1000
    rows, details = [], []
    with PeakSampler() as run_peak:
        for case in cases:
            for iteration in range(1, iterations + 1):
                row = run_paths(ocr, case_paths(case), case["reference"], case["case_id"], case["expected_summary"], iteration)
                details.append(row); rows.append({k: v for k, v in row.items() if k != "payload"})
                print(case["case_id"], iteration, row["server_pipeline_ms"], row["summary"], row["expected_correct"], flush=True)
    model_root = Path(__import__("rapidocr").__file__).resolve().parent / "models"
    models = [{"name": p.name, "bytes": p.stat().st_size, "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(model_root.glob("*.onnx"))]
    server_times = [r["server_pipeline_ms"] for r in rows]
    metadata = {
        "rapidocr": __import__("importlib.metadata").metadata.version("rapidocr"),
        "onnxruntime": __import__("importlib.metadata").metadata.version("onnxruntime"),
        "python": os.sys.version, "os": os.sys.platform, "logical_cpu_affinity": proc.cpu_affinity(),
        "intra_op_threads": 2, "inter_op_threads": 1, "init_ms": round(init_ms, 2),
        "init_peak_rss_bytes": init_peak.peak, "run_peak_rss_bytes": run_peak.peak, "models": models,
        "run_count": len(rows), "all_expected_correct": all(r["expected_correct"] for r in rows),
        "field_validation_error_count": sum(r["field_mismatch_count"] for r in rows),
        "missing_evidence_count": sum(r["missing_evidence_count"] for r in rows),
        "false_clean_count": sum(r["false_clean_count"] for r in rows),
        "false_mismatch_count": sum(r["false_mismatch_count"] for r in rows),
        "server_pipeline_p50_ms": percentile(server_times, 0.50), "server_pipeline_p95_ms": percentile(server_times, 0.95),
        "server_pipeline_max_ms": max(server_times),
    }
    (RESULTS / "details.json").write_text(json.dumps(details, indent=2), encoding="utf-8")
    (RESULTS / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    with (RESULTS / "timings.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys())); writer.writeheader(); writer.writerows(rows)
    print(json.dumps(metadata, indent=2), flush=True)
    if not metadata["all_expected_correct"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
