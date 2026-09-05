from scripts.score_product_holdout import annotated_deterministic_defects


def test_extraction_difference_is_not_a_label_compliance_defect() -> None:
    truth = {
        "brand_name": "HARBOR LIGHTS",
        "warning": {
            "present": True,
            "body_matches_statutory_text_exactly": True,
            "heading_all_caps": True,
            "heading_bold": True,
            "body_bold": False,
        },
        "imported": False,
    }

    assert annotated_deterministic_defects(truth) == []


def test_explicit_warning_and_import_defects_are_safety_signals() -> None:
    truth = {
        "warning": {
            "present": True,
            "body_matches_statutory_text_exactly": False,
            "heading_all_caps": False,
            "heading_bold": False,
            "body_bold": True,
        },
        "imported": True,
        "country_of_origin_statement": None,
    }

    assert annotated_deterministic_defects(truth) == [
        "warning_wording",
        "warning_heading_uppercase",
        "warning_heading_emphasis",
        "warning_body_not_bold",
        "country_of_origin",
    ]
