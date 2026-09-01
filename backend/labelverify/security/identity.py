from __future__ import annotations

import hashlib
import hmac
import ipaddress
import secrets
from typing import Any

from labelverify.api.errors import PublicApiError
from labelverify.settings.config import Settings

FORWARDED_HEADERS = {b"x-forwarded-for", b"x-real-ip", b"forwarded"}


class ClientIdentity:
    def __init__(self, secret: bytes | None = None) -> None:
        self._secret = secret or secrets.token_bytes(32)

    def resolve(self, scope: dict[str, Any], settings: Settings, request_id: str) -> str:
        if settings.production:
            values = _header_values(scope, b"fly-client-ip")
            if len(values) != 1 or b"," in values[0] or b"%" in values[0]:
                raise PublicApiError("invalid_client_identity", request_id)
            raw = values[0].decode("ascii", errors="strict")
        else:
            client = scope.get("client")
            raw = str(client[0]) if client else "127.0.0.1"
        try:
            normalized = ipaddress.ip_address(raw).compressed.encode("ascii")
        except (ValueError, UnicodeError) as exc:
            raise PublicApiError("invalid_client_identity", request_id) from exc
        return hmac.new(self._secret, normalized, hashlib.sha256).hexdigest()


def _header_values(scope: dict[str, Any], name: bytes) -> list[bytes]:
    return [value.strip() for key, value in scope.get("headers", []) if key.lower() == name]
