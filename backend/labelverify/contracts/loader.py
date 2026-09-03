from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from functools import cache, lru_cache
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[3]
CONTRACT_ROOT = PROJECT_ROOT / "contracts"

CONTRACT_HASHES = {
    "api-contract-v1.json": "2753b5fd2a5e6f9e6c32f2d321079cac0bfdc1660fc1a245bc38036cb451dc30",
    "error-registry-v1.json": "0e78225cbee9ae166e5d5154a231cf302051ffbb4ddc9dfc1b9a2624d9993b65",
    "selected-check-registry-v1.json": (
        "010476629434b5aaf1f1d0e522e124749cbfaaf3842116228464b34a5047f71d"
    ),
    "regulatory-rules-v1.json": (
        "30afed4b6e45b1f2bb6e8e456758f56245974f939045492540a3a199b5143149"
    ),
}


class ContractIntegrityError(RuntimeError):
    """Raised when a governed contract is missing, malformed, or changed."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


@cache
def load_contract(name: str) -> dict[str, Any]:
    expected = CONTRACT_HASHES.get(name)
    if expected is None:
        raise ContractIntegrityError(f"Unknown governed contract: {name}")
    path = CONTRACT_ROOT / name
    if not path.is_file():
        raise ContractIntegrityError(f"Governed contract is missing: {name}")
    if sha256_file(path) != expected:
        raise ContractIntegrityError(f"Governed contract hash mismatch: {name}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractIntegrityError(f"Governed contract is invalid: {name}") from exc
    if not isinstance(value, dict):
        raise ContractIntegrityError(f"Governed contract root must be an object: {name}")
    return value


@dataclass(frozen=True)
class ContractBundle:
    api: dict[str, Any]
    errors: dict[str, Any]
    checks: dict[str, Any]
    rules: dict[str, Any]

    @property
    def check_ids(self) -> tuple[str, ...]:
        return tuple(str(item["checkId"]) for item in self.checks["checks"])

    @property
    def error_codes(self) -> tuple[str, ...]:
        return tuple(str(item["code"]) for item in self.errors["errors"])


@lru_cache(maxsize=1)
def contracts() -> ContractBundle:
    bundle = ContractBundle(
        api=load_contract("api-contract-v1.json"),
        errors=load_contract("error-registry-v1.json"),
        checks=load_contract("selected-check-registry-v1.json"),
        rules=load_contract("regulatory-rules-v1.json"),
    )
    check_ids = bundle.check_ids
    error_codes = bundle.error_codes
    browser_codes = tuple(str(code) for code in bundle.errors["browserOnly"])
    if len(check_ids) != 24 or len(set(check_ids)) != 24:
        raise ContractIntegrityError("Selected-check registry must contain 24 unique checks")
    if not all(bool(item.get("aggregates")) for item in bundle.checks["checks"]):
        raise ContractIntegrityError("Every selected check must aggregate")
    if len(error_codes) != 23 or len(set(error_codes)) != 23:
        raise ContractIntegrityError("Error registry must contain 23 unique server errors")
    if len(browser_codes) != 4 or len(set(browser_codes)) != 4:
        raise ContractIntegrityError("Error registry must contain 4 unique browser errors")
    return bundle
