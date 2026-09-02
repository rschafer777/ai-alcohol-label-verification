from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import cv2
import numpy as np
import pytest
from labelverify.contracts.models import OcrLine, OriginalDimensions, PanelResult, Point
from labelverify.extraction.candidates import locate_candidates
from labelverify.imaging.decode import ImageLimitError, decode_panel
from labelverify.imaging.transforms import create_ocr_views
from PIL import Image

from .helpers import jpeg_bytes


def line(
    text: str,
    order: int,
    *,
    y: int,
    x: int = 20,
    width: int = 480,
    panel: str = "panel-1",
    height: int = 30,
    ink_density: float | None = None,
    local_contrast: float | None = 1.0,
    confidence: float = 0.95,
) -> OcrLine:
    return OcrLine(
        panelId=panel,
        text=text,
        polygon=[
            Point(x=x, y=y),
            Point(x=x + width, y=y),
            Point(x=x + width, y=y + height),
            Point(x=x, y=y + height),
        ],
        confidence=confidence,
        readingOrder=order,
        sourceView="original",
        transformId=f"transform-{panel}-v1",
        inkDensity=ink_density,
        localContrast=local_contrast,
    )


def panel() -> PanelResult:
    return PanelResult(
        panelId="panel-1",
        originalDimensions=OriginalDimensions(width=640, height=900),
        qualitySignals={"qualityClass": "Sufficient"},
        coverageState="Sufficient",
    )


def test_decode_and_bounded_views_preserve_original_coordinates(tmp_path: Path) -> None:
    path = tmp_path / "panel.jpg"
    path.write_bytes(jpeg_bytes())
    decoded = decode_panel(path, "panel-1", 12_000_000)
    assert decoded.width == 640
    assert decoded.height == 900
    decoded = replace(decoded, coverage_state="Sufficient")
    views = create_ocr_views(decoded, max_working_pixels=100_000)
    assert len(views) == 1
    assert all(view.image.shape[0] * view.image.shape[1] <= 101_000 for view in views)
    mapped = views[0].to_original_polygon([[0, 0], [10, 0], [10, 10], [0, 10]])
    assert mapped[0] == Point(x=0, y=0)
    assert all(0 <= point.x < 640 and 0 <= point.y < 900 for point in mapped)


def test_unreadable_panel_adds_bounded_enhanced_fallback(tmp_path: Path) -> None:
    path = tmp_path / "blank.png"
    Image.new("RGB", (640, 900), "white").save(path)
    decoded = decode_panel(path, "panel-1", 12_000_000)
    views = create_ocr_views(decoded, max_working_pixels=100_000)
    assert decoded.coverage_state == "Unreadable"
    assert [view.source_view for view in views] == ["derived", "derived"]
    assert views[0].transform_id.endswith("bounded-v1")
    assert views[1].transform_id.endswith("bounded-clahe-v1")
    assert all(view.image.shape[0] * view.image.shape[1] <= 101_000 for view in views)


def test_clear_trapezoid_adds_perspective_recovery_with_original_coordinate_mapping(
    tmp_path: Path,
) -> None:
    path = tmp_path / "perspective.png"
    image = np.full((900, 640, 3), 245, dtype=np.uint8)
    corners = np.asarray([[110, 100], [500, 145], [545, 700], [75, 760]], dtype=np.int32)
    cv2.polylines(image, [corners], True, (15, 15, 15), 8)
    cv2.putText(image, "OLD TOM", (165, 300), cv2.FONT_HERSHEY_SIMPLEX, 1.4, (10, 10, 10), 4)
    cv2.imwrite(str(path), cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
    decoded = replace(decode_panel(path, "panel-1", 12_000_000), coverage_state="Sufficient")

    views = create_ocr_views(decoded)

    assert len(views) == 2
    recovered = views[1]
    assert "perspective" in recovered.transform_id
    recovered_height, recovered_width = recovered.image.shape[:2]
    mapped = recovered.to_original_polygon(
        [
            [0, 0],
            [recovered_width - 1, 0],
            [recovered_width - 1, recovered_height - 1],
            [0, recovered_height - 1],
        ]
    )
    assert all(0 <= point.x < decoded.width and 0 <= point.y < decoded.height for point in mapped)
    assert min(point.x for point in mapped) < 120
    assert max(point.x for point in mapped) > 490


def test_small_angle_and_low_light_add_one_bounded_recovery_view(tmp_path: Path) -> None:
    path = tmp_path / "dark-rotated.png"
    source = np.full((500, 700, 3), 25, dtype=np.uint8)
    for y in (160, 220, 280, 340):
        cv2.line(source, (120, y), (580, y), (115, 115, 115), 5)
    matrix = cv2.getRotationMatrix2D((350, 250), 8, 1.0)
    rotated = cv2.warpAffine(source, matrix, (700, 500), borderMode=cv2.BORDER_REPLICATE)
    cv2.imwrite(str(path), cv2.cvtColor(rotated, cv2.COLOR_RGB2BGR))

    decoded = decode_panel(path, "panel-1", 12_000_000)
    views = create_ocr_views(decoded)

    assert decoded.coverage_state == "Review"
    assert abs(float(decoded.quality_signals["estimatedSkewDegrees"])) >= 1.5
    assert len(views) == 2
    assert "deskew-clahe" in views[1].transform_id


def test_decode_enforces_pixel_limit_before_transpose(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "large.png"
    Image.new("RGB", (200, 200), "white").save(path)
    transposed = False

    def fail_if_transposed(source: Image.Image) -> Image.Image:
        nonlocal transposed
        transposed = True
        return source

    monkeypatch.setattr("labelverify.imaging.decode.ImageOps.exif_transpose", fail_if_transposed)
    with pytest.raises(ImageLimitError):
        decode_panel(path, "panel-1", 39_999)
    assert not transposed


def test_candidate_location_is_reference_blind_and_typed() -> None:
    lines = [
        line("OLD TOM", 0, y=20),
        line("DISTILLERY", 1, y=54),
        line("Kentucky Straight Bourbon Whiskey", 2, y=110),
        line("45% Alc./Vol. (90 Proof)", 3, y=160),
        line("750 mL", 4, y=200),
        line("GOVERNMENT WARNING:", 5, y=260),
        line("(1) According to the Surgeon General, women should not drink", 6, y=300),
        line(
            "alcoholic beverages during pregnancy because of the risk of birth defects.", 7, y=340
        ),
        line(
            "(2) Consumption of alcoholic beverages impairs your ability to drive a car", 8, y=380
        ),
        line("or operate machinery, and may cause health problems.", 9, y=420),
        line("BOTTLED BY: OLD HERITAGE DISTILLERY, LLC", 10, y=500),
        line("FRANKFORT, KENTUCKY", 11, y=540),
    ]
    first = locate_candidates(lines, [panel()])
    second = locate_candidates(lines, [panel()])
    assert first.fields == second.fields
    assert first.field("brand").candidates[0].value == "OLD TOM DISTILLERY"
    assert first.field("class_type").status == "Found"
    assert first.field("abv").candidates[0].value.startswith("45%")
    assert first.field("proof").candidates[0].value == "90 Proof"
    assert first.field("net_contents").candidates[0].value == "750 mL"
    assert first.field("producer").status == "Found"
    assert first.warning.heading == "GOVERNMENT WARNING:"
    assert first.warning.body is not None


def test_brand_selection_is_independent_of_panel_order() -> None:
    panels = [
        panel(),
        panel().model_copy(update={"panel_id": "panel-2"}),
    ]
    first = locate_candidates(
        [
            line("SIDE PANEL", 0, y=20, height=20),
            line("ACME RESERVE", 1, y=20, panel="panel-2", height=34),
        ],
        panels,
    )
    second = locate_candidates(
        [
            line("ACME RESERVE", 0, y=20, height=34),
            line("SIDE PANEL", 1, y=20, panel="panel-2", height=20),
        ],
        panels,
    )

    assert first.field("brand").candidates[0].value == "ACME RESERVE"
    assert second.field("brand").candidates[0].value == "ACME RESERVE"

    mixed_case = locate_candidates(
        [
            line("Stone's Throw", 0, y=20, height=42),
            line("A family tradition", 1, y=78, height=18),
            line("Pinot Noir Wine", 2, y=120, height=28),
            line("Napa Valley", 3, y=165, height=46),
        ],
        [panel()],
    )
    assert mixed_case.field("brand").status == "Found"
    assert mixed_case.field("brand").candidates[0].value == "Stone's Throw"


def test_warning_body_interruption_cannot_become_brand() -> None:
    observed = locate_candidates(
        [
            line("ACME RESERVE", 0, y=20, height=30),
            line("GOVERNMENT WARNING:", 1, y=100, height=30),
            line("(1) Required warning text", 2, y=140, height=30),
            line("ACME QUALITY SINCE 1998", 3, y=180, height=34),
            line("(2) Required warning text", 4, y=225, height=30),
        ],
        [panel()],
    )

    assert observed.field("brand").candidates[0].value == "ACME RESERVE"
    assert observed.warning.continuous is False


def test_uppercase_warning_body_is_not_treated_as_an_interruption() -> None:
    observed = locate_candidates(
        [
            line("GOVERNMENT WARNING:", 0, y=100, ink_density=0.4),
            line("(1) ACCORDING TO THE SURGEON GENERAL, WOMEN SHOULD NOT", 1, y=140),
            line("DRINK ALCOHOLIC BEVERAGES DURING PREGNANCY", 2, y=180),
            line("(2) CONSUMPTION OF ALCOHOLIC BEVERAGES IMPAIRS", 3, y=220),
            line("YOUR ABILITY TO OPERATE MACHINERY AND MAY CAUSE HEALTH PROBLEMS.", 4, y=260),
        ],
        [panel()],
    )

    assert observed.warning.body is not None
    assert "DRINK ALCOHOLIC BEVERAGES" in observed.warning.body
    assert "(2) CONSUMPTION" in observed.warning.body
    assert observed.warning.continuous is True


def test_inline_second_clause_and_large_caption_gap_support_structure() -> None:
    observed = locate_candidates(
        [
            line("BACK LABEL", 0, y=20, height=20),
            line("GOVERNMENT WARNING: (1) Required warning text", 1, y=100),
            line("continuation text. (2)", 2, y=140),
            line("Required warning text and may cause health problems.", 3, y=180),
        ],
        [panel()],
    )

    assert observed.warning.separated is True
    assert observed.warning.continuous is True


def test_warning_extraction_uses_the_heading_column_not_interleaved_front_text() -> None:
    observed = locate_candidates(
        [
            line("FRONT BRAND", 0, y=20, x=20, width=220, height=60),
            line("GOVERNMENT WARNING:", 1, y=100, x=360, width=240, ink_density=0.4),
            line("47% Alc./Vol. (94 Proof)", 2, y=140, x=20, width=220),
            line("(1) Required warning text.", 3, y=140, x=360, width=260),
            line("1 Liter", 4, y=180, x=20, width=220),
            line(
                "(2) Required warning text and may cause health problems.",
                5,
                y=180,
                x=360,
                width=260,
            ),
        ],
        [panel()],
    )

    assert observed.warning.body == (
        "(1) Required warning text. (2) Required warning text and may cause health problems."
    )
    assert "47%" not in observed.warning.body
    assert observed.warning.heading_bold is True


def test_abv_requires_alcohol_context_and_ignores_composition_percentages() -> None:
    observed = locate_candidates(
        [
            line("100% BLUE AGAVE REPOSADO TEQUILA", 0, y=20),
            line("40% Alc./Vol. (80 Proof)", 1, y=60),
        ],
        [panel()],
    )

    assert observed.field("abv").status == "Found"
    assert [item.value for item in observed.field("abv").candidates] == ["40%"]


def test_class_type_excludes_producer_names_and_composite_footer_lines() -> None:
    observed = locate_candidates(
        [
            line("LONDON DRY GIN", 0, y=20),
            line("Imported by Clearwater Spirits, Austin, Texas", 1, y=60),
            line("1 Liter 47% Alc./Vol. (94 Proof) London Dry Gin", 2, y=100),
        ],
        [panel()],
    )

    assert observed.field("class_type").status == "Found"
    assert [item.value for item in observed.field("class_type").candidates] == ["LONDON DRY GIN"]


def test_conflicting_country_candidates_keep_distinct_regions() -> None:
    lines = [
        line("PRODUCT OF CANADA", 0, y=100),
        line("IMPORTED FROM FRANCE", 1, y=200),
    ]
    observed = locate_candidates(lines, [panel()])
    country = observed.field("country")
    assert country.status == "Ambiguous"
    assert {item.value for item in country.candidates} == {"CANADA", "FRANCE"}
    assert len({item.evidence.evidence_id for item in country.candidates}) == 2
    assert (
        len(
            {
                tuple((point.x, point.y) for point in item.evidence.polygon_original_pixels)
                for item in country.candidates
            }
        )
        == 2
    )


def test_blank_image_is_not_reported_as_sufficient(tmp_path: Path) -> None:
    path = tmp_path / "blank.png"
    Image.new("RGB", (300, 300), "white").save(path)
    decoded = decode_panel(path, "panel-1", 12_000_000)
    assert decoded.coverage_state == "Unreadable"


def test_unreadable_panel_cannot_create_plausible_field_candidates() -> None:
    unreadable = panel().model_copy(update={"coverage_state": "Unreadable"})
    observed = locate_candidates(
        [
            line("WRONG BRAND", 0, y=20),
            line("12% Alc./Vol.", 1, y=60),
            line("375 mL", 2, y=100),
        ],
        [unreadable],
    )

    assert observed.field("brand").status == "Unreadable"
    assert observed.field("abv").status == "Unreadable"
    assert observed.field("net_contents").status == "Unreadable"
    assert observed.warning.source_unreadable is True
    assert observed.evidence == []


def test_ocr_text_claiming_a_scale_is_not_treated_as_calibrated_measurement() -> None:
    lines = [
        line("GOVERNMENT WARNING:", 0, y=100),
        line("(1) Required warning body", 1, y=140),
        line("SYNTHETIC SCALE: 2 mm", 2, y=220),
    ]

    observed = locate_candidates(lines, [panel()])

    assert observed.warning.physical_size_mm is None
    assert observed.warning.characters_per_inch is None
    assert observed.warning.reliable_scale is False
    assert observed.warning.scale_evidence is None
    assert all(item.text_snippet != "SYNTHETIC SCALE: 2 mm" for item in observed.evidence)


def test_warning_line_join_marks_punctuation_at_lowercase_wrap_as_uncertain() -> None:
    observed = locate_candidates(
        [
            line("GOVERNMENT WARNING:", 0, y=100),
            line("(1) First required sentence.", 1, y=140),
            line("women should not drink alcohol.", 2, y=180),
        ],
        [panel()],
    )

    assert observed.warning.body == "(1) First required sentence women should not drink alcohol."
    assert observed.warning.punctuation_normalized is True


def test_warning_heading_requires_a_separator_between_words() -> None:
    observed = locate_candidates(
        [
            line("GOVERNMENTWARNING:", 0, y=100),
            line("(1) Required warning body", 1, y=140),
        ],
        [panel()],
    )

    assert observed.warning.heading is None
    assert observed.warning.body is None


def test_imports_name_anchors_imported_producer_and_address() -> None:
    observed = locate_candidates(
        [
            line("RIVER ROAD IMPORTS", 0, y=100),
            line("LOUISVILLE, KENTUCKY 40202", 1, y=140),
            line("GOVERNMENT WARNING:", 2, y=200),
        ],
        [panel()],
    )

    producer = observed.field("producer")
    assert producer.status == "Found"
    assert producer.candidates[0].value == ("RIVER ROAD IMPORTS LOUISVILLE, KENTUCKY 40202")


def test_warning_presentation_signals_remain_independent() -> None:
    normal_body = [
        line(
            "(1) According to the Surgeon General, women should not drink",
            2,
            y=180,
            height=32,
            ink_density=0.2,
        ),
        line(
            "(2) Consumption of alcoholic beverages impairs your ability.",
            3,
            y=220,
            height=32,
            ink_density=0.2,
        ),
    ]
    observed = locate_candidates(
        [
            line("FRANKFORT, KENTUCKY 40601", 0, y=100, height=22),
            line(
                "Government Warning:.",
                1,
                y=145,
                height=32,
                ink_density=0.27,
            ),
            *normal_body,
        ],
        [panel()],
    )

    assert observed.warning.heading == "Government Warning:."
    assert observed.warning.body is not None
    assert observed.warning.body.startswith("(1)")
    assert observed.warning.heading_bold is True
    assert observed.warning.body_bold is False
    assert observed.warning.separated is True
    assert observed.warning.continuous is True
    assert observed.warning.contrast_sufficient is True
    assert observed.warning.legible is True


def test_warning_style_heuristics_detect_known_failures_and_uncertainty() -> None:
    low_contrast = locate_candidates(
        [
            line("FRANKFORT, KENTUCKY 40601", 0, y=100, height=22),
            line(
                "GOVERNMENT WARNING:",
                1,
                y=145,
                height=29,
                ink_density=None,
            ),
            line(
                "(1) Required warning text",
                2,
                y=190,
                height=32,
                ink_density=None,
            ),
            line(
                "(2) Required warning text",
                3,
                y=230,
                height=32,
                ink_density=None,
            ),
        ],
        [panel()],
    ).warning
    assert low_contrast.heading_bold is None
    assert low_contrast.body_bold is None
    assert low_contrast.contrast_sufficient is None
    assert low_contrast.legible is None

    plain_heading = locate_candidates(
        [
            line("FRANKFORT, KENTUCKY 40601", 0, y=100, height=22),
            line(
                "GOVERNMENT WARNING:",
                1,
                y=145,
                height=23,
                ink_density=0.299,
            ),
            line("(1) Required warning text", 2, y=190, ink_density=0.2),
            line("(2) Required warning text", 3, y=230, ink_density=0.2),
        ],
        [panel()],
    ).warning
    assert plain_heading.heading_bold is False

    bold_body = locate_candidates(
        [
            line("FRANKFORT, KENTUCKY 40601", 0, y=100, height=22),
            line("GOVERNMENT WARNING:", 1, y=145, height=30, ink_density=0.4),
            line("(1) Required warning text", 2, y=190, ink_density=0.65),
            line("(2) Required warning text..", 3, y=230, ink_density=0.65),
        ],
        [panel()],
    ).warning
    assert bold_body.body_bold is True
    assert bold_body.body is not None and bold_body.body.endswith("text..")

    uncertain_separation = locate_candidates(
        [
            line("BOTTLED FOR REVIEW", 0, y=100, height=22),
            line("GOVERNMENT WARNING:", 1, y=150, height=30, ink_density=0.4),
            line("(1) Required warning text", 2, y=195, ink_density=0.2),
            line("(2) Required warning text", 3, y=235, ink_density=0.2),
        ],
        [panel()],
    ).warning
    assert uncertain_separation.separated is None


def test_missing_or_distant_surrounding_text_cannot_prove_separation() -> None:
    no_previous = locate_candidates(
        [
            line("GOVERNMENT WARNING:", 0, y=160, ink_density=0.4),
            line("(1) Required warning text", 1, y=200, ink_density=0.2),
            line("(2) Required warning text", 2, y=240, ink_density=0.2),
        ],
        [panel()],
    ).warning
    distant_previous = locate_candidates(
        [
            line("BACK LABEL", 0, y=20, height=20, ink_density=0.2),
            line("GOVERNMENT WARNING:", 1, y=200, ink_density=0.4),
            line("(1) Required warning text", 2, y=240, ink_density=0.2),
            line("(2) Required warning text", 3, y=280, ink_density=0.2),
        ],
        [panel()],
    ).warning

    assert no_previous.separated is None
    assert distant_previous.separated is None
    assert distant_previous.heading_bold is True


def test_regular_inverse_polarity_signal_is_not_mistaken_for_bold() -> None:
    observed = locate_candidates(
        [
            line("GOVERNMENT WARNING:", 0, y=100, ink_density=0.2),
            line("(1) Required warning text", 1, y=140, ink_density=0.2),
            line("(2) Required warning text", 2, y=180, ink_density=0.2),
        ],
        [panel()],
    ).warning

    assert observed.heading_bold is None
    assert observed.body_bold is False
    assert observed.contrast_sufficient is True


def test_low_absolute_heading_density_needs_relative_evidence_to_fail() -> None:
    observed = locate_candidates(
        [
            line("GOVERNMENT WARNING:(1) According", 0, y=100, ink_density=0.24),
            line("to the Surgeon General", 1, y=140, ink_density=0.18),
            line("(2) Consumption of alcoholic beverages", 2, y=180, ink_density=0.18),
        ],
        [panel()],
    ).warning

    assert observed.heading_bold is None


def test_warning_interruption_changes_continuity_without_changing_body_wording() -> None:
    observed = locate_candidates(
        [
            line("FRANKFORT, KENTUCKY 40601", 0, y=100, height=22),
            line("GOVERNMENT WARNING:", 1, y=145, height=30, ink_density=0.4),
            line("(1) Required warning text.", 2, y=190, ink_density=0.2),
            line("PROMOTIONAL MESSAGE", 3, y=230, ink_density=0.4),
            line("(2) Required warning text.", 4, y=270, ink_density=0.2),
        ],
        [panel()],
    ).warning

    assert observed.continuous is False
    assert observed.body == "(1) Required warning text. (2) Required warning text."


def test_ocr_corrupted_uppercase_warning_words_are_not_interruptions() -> None:
    observed = locate_candidates(
        [
            line("GOVERNMENT WARNING:", 0, y=100, ink_density=0.4),
            line("(1) ACCORDING TO THE SURGEON GENERAL", 1, y=140, ink_density=0.2),
            line("PREGMANCY BECAUSE OFTHERISK OF BRTH DEFECTS", 2, y=180, ink_density=0.2),
            line("(2) CONSUMPTION OF ALCOHOLIC BEVERAGES", 3, y=220, ink_density=0.2),
            line("MACHINERY AND MAY CAUSE HEALTH PROBLEMS", 4, y=260, ink_density=0.2),
        ],
        [panel()],
    ).warning

    assert observed.continuous is True
    assert observed.body is not None
    assert "PREGMANCY" in observed.body


def test_warning_interruption_after_second_clause_cannot_preserve_continuity() -> None:
    observed = locate_candidates(
        [
            line("GOVERNMENT WARNING:", 0, y=100, ink_density=0.4),
            line("(1) First required sentence.", 1, y=140, ink_density=0.2),
            line("(2) Second required sentence", 2, y=180, ink_density=0.2),
            line("PROMOTIONAL MESSAGE", 3, y=220, ink_density=0.4),
            line("and may cause health problems.", 4, y=260, ink_density=0.2),
        ],
        [panel()],
    ).warning

    assert observed.continuous is False
    assert observed.body == (
        "(1) First required sentence. (2) Second required sentence and may cause health problems."
    )
