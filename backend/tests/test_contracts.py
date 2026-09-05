from __future__ import annotations

import hashlib

import pytest
from labelverify.api.errors import LOCATOR_ALLOWED, PublicApiError, error_map
from labelverify.contracts.loader import (
    CONTRACT_HASHES,
    ContractIntegrityError,
    contracts,
    sha256_file,
)
from labelverify.contracts.models import CorrectionRequest, ReferenceRecord


def test_cg001_hashes_and_counts() -> None:
    bundle = contracts()
    for name, expected in CONTRACT_HASHES.items():
        assert sha256_file(__import__("pathlib").Path("contracts") / name) == expected
    assert len(bundle.check_ids) == len(set(bundle.check_ids)) == 24
    assert sum(value.startswith("warning_") for value in bundle.check_ids) == 10
    assert len(bundle.error_codes) == len(set(bundle.error_codes)) == 27
    assert len(bundle.errors["browserOnly"]) == 4


def test_governed_text_hash_is_stable_across_line_endings(tmp_path) -> None:
    contract = tmp_path / "contract.json"
    contract.write_bytes(b'{\r\n  "version": 1\r\n}\r\n')

    assert sha256_file(contract) == hashlib.sha256(b'{\n  "version": 1\n}\n').hexdigest()


def test_public_error_registry_is_exhaustive_and_result_free() -> None:
    assert set(error_map()) == set(contracts().error_codes)
    for code, row in error_map().items():
        error = PublicApiError(code, "opaque", "panel-1")
        payload = error.public()
        assert error.http_status == row["http"]
        assert payload.retryable is row["retryable"]
        assert payload.next_action == row["action"]
        assert not hasattr(payload, "result")
        assert (payload.field_or_panel is not None) is (code in LOCATOR_ALLOWED)


def test_unknown_error_falls_back_to_internal_error() -> None:
    error = PublicApiError("unknown", "request")
    assert error.code == "internal_error"
    assert error.http_status == 500


def test_reference_requires_import_origin() -> None:
    base = {
        "profileId": "all_beverages_demo_v2",
        "beverageType": "distilled_spirits",
        "referenceProvenance": "manual",
        "brandName": "Brand",
        "classType": "Whiskey",
        "abvPercent": 45,
        "netContentsValue": 750,
        "netContentsUnit": "mL",
        "producerNameAddress": "Producer",
        "isImported": True,
    }
    with pytest.raises(ValueError):
        ReferenceRecord.model_validate(base)


def test_unknown_contract_is_rejected() -> None:
    from labelverify.contracts.loader import load_contract

    with pytest.raises(ContractIntegrityError):
        load_contract("not-governed.json")


def test_correction_contract_is_field_specific_and_requires_one_locator() -> None:
    beverage = CorrectionRequest.model_validate(
        {
            "expectedRevision": 1,
            "reason": "Visible label correction",
            "corrections": [
                {
                    "field": "beverage_type",
                    "family": "wine",
                    "evidenceRef": "ev_type_panel-1_01",
                }
            ],
        }
    )
    assert beverage.corrections[0].field == "beverage_type"

    producer = CorrectionRequest.model_validate(
        {
            "expectedRevision": 1,
            "reason": "Visible label correction",
            "corrections": [
                {
                    "field": "producer_name_address",
                    "visibleText": "BOTTLED BY PRODUCER\nDENVER, COLORADO",
                    "panelId": "panel-1",
                    "polygon": [
                        {"x": 1, "y": 1},
                        {"x": 100, "y": 1},
                        {"x": 100, "y": 50},
                        {"x": 1, "y": 50},
                    ],
                }
            ],
        }
    )
    assert producer.corrections[0].field == "producer_name_address"

    invalid_payloads = [
        {
            "field": "brand_name",
            "visibleText": "BRAND",
        },
        {
            "field": "brand_name",
            "visibleText": "BRAND",
            "evidenceRef": "ev_brand_panel-1_01",
            "panelId": "panel-1",
            "polygon": [{"x": 1, "y": 1}] * 4,
        },
        {
            "field": "beverage_type",
            "visibleText": "Wine",
            "evidenceRef": "ev_type_panel-1_01",
        },
        {
            "field": "producer_name_address",
            "visibleText": "1\n2\n3\n4\n5\n6",
            "evidenceRef": "ev_producer_panel-1_01",
        },
    ]
    for correction in invalid_payloads:
        with pytest.raises(ValueError):
            CorrectionRequest.model_validate(
                {
                    "expectedRevision": 1,
                    "reason": "Visible label correction",
                    "corrections": [correction],
                }
            )
