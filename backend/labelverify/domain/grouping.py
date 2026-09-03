"""Server-side batch grouping suggestions (handoff REQ-14).

Images are analyzed one at a time by ``POST /api/v1/analyses``; the client then submits the
label-derived facts of every image here and receives one suggested product per group. The
suggestion is deliberately conservative: images join a product only when they share a folder
or a readable brand, never on image similarity, and a group never exceeds three panels.
"""

from __future__ import annotations

import re
from collections import OrderedDict
from difflib import SequenceMatcher
from itertools import combinations
from typing import Literal

from labelverify.contracts.models import GroupingImage, GroupingResult, GroupSuggestion

MAX_PANELS = 3
_ROLE_WORDS = re.compile(
    r"(?:^|[-_.\s])(front|back|rear|neck|side|panel|label|left|right|photo|image|img)"
    r"(?=[-_.\s]|$)",
    re.I,
)
_NON_WORD = re.compile(r"[^a-z0-9]+")


def _brand_key(value: str | None) -> str:
    if not value:
        return ""
    return _NON_WORD.sub(" ", value.casefold()).strip()


def _class_key(value: str | None) -> str:
    if not value:
        return ""
    return _NON_WORD.sub(" ", value.casefold()).strip()


def _folder_key(image: GroupingImage) -> str | None:
    path = (image.path or "").replace("\\", "/")
    parts = [part for part in path.split("/") if part]
    if len(parts) > 2:
        return "/".join(parts[:-1]).casefold()
    return None


def _stem_key(image: GroupingImage) -> str:
    stem = re.sub(r"\.[^.]+$", "", image.file_name)
    normalized = _ROLE_WORDS.sub(" ", stem)
    normalized = re.sub(r"[-_.\s]+", " ", normalized).strip().casefold()
    return normalized or stem.casefold()


def _display_name(images: list[GroupingImage], ordinal: int) -> str:
    """Prefer the brand read on the image that also carried a beverage-type signal.

    The front panel usually names the class or type; a back or side panel more often yields
    OCR noise, so its brand should not name the product when a better read exists.
    """

    candidates = [image for image in images if image.brand_name and image.brand_name.strip()]
    brand_keys = {_brand_key(image.brand_name) for image in candidates}
    if candidates and _brands_are_compatible(brand_keys):
        return (
            max(candidates, key=lambda image: len(_brand_key(image.brand_name))).brand_name or ""
        ).strip()

    ranked = sorted(
        candidates,
        key=lambda image: (
            image.beverage_type is None,
            {"high": 0, "medium": 1, "low": 2, None: 3}[image.type_confidence],
            -len(_brand_key(image.brand_name)),
        ),
    )
    if ranked:
        return (ranked[0].brand_name or "").strip()
    return f"Product {ordinal}"


def _brands_are_compatible(values: set[str]) -> bool:
    """Whether several brand reads can describe one product.

    A shorter read contained in a fuller read is compatible ("VALLE" in "VALLE DI PIETRA"),
    and so are reads that share a distinctive word or word stem ("JACK DANIEL'S" on the front
    and "JACK DANIEL DISTILLERY" on the back). Reads with nothing in common stay a conflict.
    """

    if len(values) <= 1:
        return True
    compact = {_NON_WORD.sub("", value.casefold()) for value in values}
    longest = max(compact, key=len)
    if all(len(value) >= 4 and value in longest for value in compact):
        return True
    # Reads of one brand damaged by OCR ("HARBOR LIGHTSE" beside "HARBOR LIGHTS") stay
    # close as strings, and a fuller form of one name shares its opening word ("JACK
    # DANIEL'S" beside "JACK DANIEL DISTILLERY"). A shared opening word alone ("SILVER OAK"
    # beside "SILVER SPRINGS BREWING") is two brands.
    first_words = {value.split()[0].casefold() for value in values if value.split()}
    shared_opening = len(first_words) == 1 and len(next(iter(first_words))) >= 4
    floor = 0.6 if shared_opening else 0.8
    return all(
        SequenceMatcher(None, left, right, autojunk=False).ratio() >= floor
        for left, right in combinations(sorted(compact), 2)
    )


def _confidence(images: list[GroupingImage]) -> Literal["high", "medium", "low"]:
    levels = [image.type_confidence for image in images if image.type_confidence]
    if not levels:
        return "low"
    if all(level == "high" for level in levels):
        return "high"
    if any(level == "low" for level in levels):
        return "low"
    return "medium"


def suggest_groups(images: list[GroupingImage]) -> GroupingResult:
    usable = [image for image in images if not image.failed]
    failed = len(images) - len(usable)
    ordered = sorted(usable, key=lambda item: (item.path or item.file_name).casefold())

    # Pass 1: bucket by folder when a useful hierarchy exists, otherwise by filename stem.
    buckets: OrderedDict[str, list[GroupingImage]] = OrderedDict()
    for image in ordered:
        folder = _folder_key(image)
        key = f"folder:{folder}" if folder else f"stem:{_stem_key(image)}"
        buckets.setdefault(key, []).append(image)

    # Pass 2: merge loose buckets that read the same product identity. A folder is an explicit
    # statement of intent and remains isolated. Loose images can be separated by unrelated
    # filenames, so they merge globally when their brand matches and any readable class agrees.
    merged: list[tuple[list[GroupingImage], list[str], bool]] = []
    loose_brand_indexes: dict[str, list[int]] = {}
    for key, bucket in buckets.items():
        reasons: list[str] = []
        is_folder = key.startswith("folder:")
        if is_folder:
            reasons.append("Same folder")
        elif len(bucket) > 1:
            reasons.append("Filename cues match")
        brand = next(
            (_brand_key(item.brand_name) for item in bucket if _brand_key(item.brand_name)), ""
        )
        if brand and not is_folder:
            candidate_index = next(
                (
                    index
                    for index in loose_brand_indexes.get(brand, [])
                    if _classes_are_compatible(merged[index][0], bucket)
                ),
                None,
            )
            if candidate_index is not None:
                previous_images, previous_reasons, _ = merged[candidate_index]
                previous_images.extend(bucket)
                if "Same brand and compatible class read" not in previous_reasons:
                    previous_reasons.append("Same brand and compatible class read")
                continue
        merged.append((bucket, reasons, is_folder))
        if brand and not is_folder:
            loose_brand_indexes.setdefault(brand, []).append(len(merged) - 1)

    groups: list[GroupSuggestion] = []
    ordinal = 0
    for bucket, reasons, _ in merged:
        for offset in range(0, len(bucket), MAX_PANELS):
            chunk = bucket[offset : offset + MAX_PANELS]
            ordinal += 1
            groups.append(_suggestion(chunk, list(reasons), ordinal, len(bucket) > MAX_PANELS))
    return GroupingResult(groups=groups, analyzed=len(usable), failed=failed)


def _classes_are_compatible(first: list[GroupingImage], second: list[GroupingImage]) -> bool:
    values = {
        _class_key(image.class_type) for image in [*first, *second] if _class_key(image.class_type)
    }
    return len(values) <= 1


def _suggestion(
    chunk: list[GroupingImage], reasons: list[str], ordinal: int, overflow: bool
) -> GroupSuggestion:
    brands = {_brand_key(item.brand_name) for item in chunk if _brand_key(item.brand_name)}
    types = {item.beverage_type for item in chunk if item.beverage_type}
    conflict = not _brands_are_compatible(brands) or len(types) > 1
    confidence = _confidence(chunk)
    status: Literal["ready_to_confirm", "needs_review"]
    if conflict:
        if not _brands_are_compatible(brands):
            reasons.append("Two different brands read")
        if len(types) > 1:
            reasons.append("Different beverage types read")
        status = "needs_review"
    elif overflow:
        reasons.append("More than three images; split into products")
        status = "needs_review"
    elif not brands:
        reasons.append("Brand not read; confirm this product")
        status = "needs_review"
    elif confidence == "low" or not types:
        reasons.append("Beverage type uncertain; confirm the type")
        status = "needs_review"
    else:
        if len(chunk) == 1:
            reasons.append("One image, one product")
        status = "ready_to_confirm"
    inferred = next(iter(types)) if len(types) == 1 else None
    return GroupSuggestion(
        groupId=f"group-{ordinal}",
        panelIds=[item.image_id for item in chunk],
        suggestedName=_display_name(chunk, ordinal),
        inferredType=inferred,
        confidence=confidence,
        status=status,
        reasons=reasons,
        conflict=conflict,
    )
