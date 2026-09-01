from __future__ import annotations

import pytest
from labelverify.api.errors import LOCATOR_ALLOWED, PublicApiError, error_map
from labelverify.contracts.loader import (
    CONTRACT_HASHES,
    ContractIntegrityError,
    contracts,
    sha256_file,
)
from labelverify.contracts.models import ReferenceRecord


def test_cg001_hashes_and_counts() -> None:
    bundle = contracts()
    for name, expected in CONTRACT_HASHES.items():
        assert sha256_file(__import__("pathlib").Path("contracts") / name) == expected
    assert len(bundle.check_ids) == len(set(bundle.check_ids)) == 19
    assert sum(value.startswith("warning_") for value in bundle.check_ids) == 10
    assert len(bundle.error_codes) == len(set(bundle.error_codes)) == 23
    assert len(bundle.errors["browserOnly"]) == 4


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
        "profileId": "distilled_spirits_demo_v1",
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
