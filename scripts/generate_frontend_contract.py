"""Validate the CG-004 frontend copy against the four root contracts.

This command is intentionally read-only. Root remains the only role allowed to
update frontend/src/api/generated-contract.ts.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def expected_contract_data(project_root: Path) -> dict[str, Any]:
    contracts = project_root / "contracts"
    api = load_json(contracts / "api-contract-v1.json")
    checks = load_json(contracts / "selected-check-registry-v1.json")
    errors = load_json(contracts / "error-registry-v1.json")
    regulatory = load_json(contracts / "regulatory-rules-v1.json")
    check_ids = [row["checkId"] for row in checks["checks"]]
    server_codes = [row["code"] for row in errors["errors"]]
    browser_codes = list(errors["browserOnly"])
    if len(check_ids) != 19 or len(set(check_ids)) != 19:
        raise ValueError("Selected-check registry must contain 19 unique checks")
    if len(server_codes) != 23 or len(set(server_codes)) != 23:
        raise ValueError("Server error registry must contain 23 unique codes")
    if len(browser_codes) != 4 or len(set(browser_codes)) != 4:
        raise ValueError("Browser error registry must contain 4 unique codes")
    versions = {
        api["contractVersion"],
        checks["registryVersion"],
        errors["registryVersion"],
        regulatory["registryVersion"],
    }
    if versions != {"1.0.0"}:
        raise ValueError(f"CG-001 versions differ: {sorted(versions)}")
    return {
        "contractVersion": api["contractVersion"],
        "profileId": api["$defs"]["Reference"]["properties"]["profileId"]["const"],
        "limits": api["limits"],
        "checkIds": check_ids,
        "serverErrorCodes": server_codes,
        "browserErrorCodes": browser_codes,
    }


def extract_string(text: str, name: str) -> str | None:
    match = re.search(
        rf'export\s+const\s+{re.escape(name)}\s*=\s*"([^"]+)"\s+as\s+const', text
    )
    return match.group(1) if match else None


def extract_string_array(text: str, name: str) -> list[str] | None:
    match = re.search(
        rf"export\s+const\s+{re.escape(name)}\s*=\s*(\[.*?\])\s+as\s+const",
        text,
        re.DOTALL,
    )
    if not match:
        return None
    return json.loads(match.group(1))


def extract_limits(text: str, expected_keys: set[str]) -> dict[str, int | float] | None:
    match = re.search(
        r"export\s+const\s+limits\s*=\s*\{(.*?)\}\s+as\s+const",
        text,
        re.DOTALL,
    )
    if not match:
        return None
    values: dict[str, int | float] = {}
    pattern = r"([A-Za-z][A-Za-z0-9]*)\s*:\s*([0-9_]+(?:\.[0-9]+)?)"
    for key, raw in re.findall(pattern, match.group(1)):
        cleaned = raw.replace("_", "")
        values[key] = float(cleaned) if "." in cleaned else int(cleaned)
    if set(values) != expected_keys:
        return values
    return values


def validate_frontend_contract(project_root: Path) -> list[str]:
    errors: list[str] = []
    expected = expected_contract_data(project_root)
    target = project_root / "frontend" / "src" / "api" / "generated-contract.ts"
    if not target.exists():
        return [f"Generated frontend contract is missing: {target}"]
    text = target.read_text(encoding="utf-8")
    if extract_string(text, "contractVersion") != expected["contractVersion"]:
        errors.append("contractVersion differs from api-contract-v1.json")
    if extract_string(text, "profileId") != expected["profileId"]:
        errors.append("profileId differs from api-contract-v1.json")
    if extract_limits(text, set(expected["limits"])) != expected["limits"]:
        errors.append("limits differ from api-contract-v1.json")
    if extract_string_array(text, "checkIds") != expected["checkIds"]:
        errors.append("checkIds differ from selected-check-registry-v1.json")
    if extract_string_array(text, "serverErrorCodes") != expected["serverErrorCodes"]:
        errors.append("serverErrorCodes differ from error-registry-v1.json")
    if extract_string_array(text, "browserErrorCodes") != expected["browserErrorCodes"]:
        errors.append("browserErrorCodes differ from error-registry-v1.json")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--print-expected", action="store_true")
    args = parser.parse_args()
    project_root = Path(__file__).resolve().parents[1]
    if args.print_expected:
        print(json.dumps(expected_contract_data(project_root), indent=2, sort_keys=True))
        return 0
    errors = validate_frontend_contract(project_root)
    print(json.dumps({"errors": errors, "pass": not errors}, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
