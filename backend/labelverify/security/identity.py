from __future__ import annotations

import hashlib
import hmac
import ipaddress
import secrets
from typing import Any

from labelverify.api.errors import PublicApiError
from labelverify.settings.config import Settings


class ClientIdentity:
    def __init__(self, secret: bytes | None = None) -> None:
        self._secret = secret or secrets.token_bytes(32)

    def resolve(self, scope: dict[str, Any], settings: Settings, request_id: str) -> str:
        if settings.production:
            raw = _trusted_production_ip(scope, settings, request_id)
        else:
            client = scope.get("client")
            raw = str(client[0]) if client else "127.0.0.1"
        try:
            normalized = ipaddress.ip_address(raw).compressed.encode("ascii")
        except (ValueError, UnicodeError) as exc:
            raise PublicApiError("invalid_client_identity", request_id) from exc
        return hmac.new(self._secret, normalized, hashlib.sha256).hexdigest()


def _trusted_production_ip(scope: dict[str, Any], settings: Settings, request_id: str) -> str:
    if settings.client_identity_source == "fly":
        values = _header_values(scope, b"fly-client-ip")
        if len(values) != 1 or b"," in values[0] or b"%" in values[0]:
            raise PublicApiError("invalid_client_identity", request_id)
        candidate = values[0]
    elif settings.client_identity_source == "azure_container_apps":
        values = _header_values(scope, b"x-forwarded-for")
        if len(values) != 1:
            raise PublicApiError("invalid_client_identity", request_id)
        candidate = values[0].rsplit(b",", 1)[-1].strip()
        if not candidate or b"%" in candidate:
            raise PublicApiError("invalid_client_identity", request_id)
    else:
        raise PublicApiError("invalid_client_identity", request_id)
    try:
        return candidate.decode("ascii", errors="strict")
    except UnicodeError as exc:
        raise PublicApiError("invalid_client_identity", request_id) from exc


def _header_values(scope: dict[str, Any], name: bytes) -> list[bytes]:
    return [value.strip() for key, value in scope.get("headers", []) if key.lower() == name]
