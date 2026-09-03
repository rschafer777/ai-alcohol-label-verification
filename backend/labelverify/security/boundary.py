from __future__ import annotations

import asyncio
import re
import secrets
import time
import uuid
from http.cookies import SimpleCookie
from typing import Any

from starlette.responses import JSONResponse

from labelverify.api.errors import PublicApiError
from labelverify.contracts.loader import contracts
from labelverify.security.identity import ClientIdentity, _header_values
from labelverify.security.rate_limit import AdmissionController, StartRateLimiter
from labelverify.settings.config import Settings

VERIFY_PATH = "/api/v1/verifications"
ANALYZE_PATH = "/api/v1/analyses"
GROUPING_PATH = "/api/v1/grouping-suggestions"
EXPENSIVE_PATHS = frozenset({VERIFY_PATH, ANALYZE_PATH})
HISTORY_PATH = "/api/v1/history"
# POST /api/v1/history/{record_id}/panels re-runs OCR on a stored record plus one new image.
HISTORY_PANEL_ADD_PATTERN = re.compile(r"/api/v1/history/hist_[0-9a-f]+/panels\Z")
HISTORY_SCOPE_COOKIE = "labelverify_scope"
HISTORY_SCOPE_PATTERN = re.compile(r"[A-Za-z0-9_-]{43}\Z")
HISTORY_SCOPE_MAX_AGE = 7 * 24 * 60 * 60
JSON_BODY_LIMIT = 8 * 1024


class BoundaryMiddleware:
    def __init__(
        self,
        app: Any,
        settings: Settings,
        *,
        identity: ClientIdentity | None = None,
        limiter: StartRateLimiter | None = None,
        admissions: AdmissionController | None = None,
    ) -> None:
        self.app = app
        self.settings = settings
        self.identity = identity or ClientIdentity()
        self.limiter = limiter or StartRateLimiter()
        self.admissions = admissions or AdmissionController()
        limits = contracts().api["limits"]
        self.raw_limit = int(limits["rawRequestBytes"])
        self.grouping_body_limit = int(limits["groupingRequestBytes"])
        self.upload_deadline = float(limits["uploadDeadlineSeconds"])
        self.server_deadline = float(limits["serverDeadlineSeconds"])

    async def __call__(self, scope: dict[str, Any], receive: Any, send: Any) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        request_id = uuid.uuid4().hex
        scope.setdefault("state", {})["request_id"] = request_id
        history_scope_id, set_history_cookie = _history_scope(scope)
        scope["state"]["history_scope_id"] = history_scope_id
        started = time.monotonic()
        response_started = False

        async def secure_send(message: dict[str, Any]) -> None:
            nonlocal response_started
            if message["type"] == "http.response.start":
                response_started = True
                headers = _security_headers(
                    list(message.get("headers", [])),
                    production=self.settings.production,
                    no_store=scope.get("path", "").startswith("/api/")
                    or scope.get("path", "").startswith("/health/"),
                )
                if set_history_cookie and scope.get("path", "").startswith("/api/"):
                    headers.append(
                        (
                            b"set-cookie",
                            _scope_cookie(history_scope_id, self.settings.production),
                        )
                    )
                message["headers"] = headers
            await send(message)

        client_key: str | None = None
        rate_started = False
        admitted = False
        try:
            self._validate_host_origin(scope, request_id)
            expensive = _is_expensive(scope)
            mutation = _is_state_change(scope)
            if expensive or mutation:
                client_key = self.identity.resolve(scope, self.settings, request_id)
                body_limit = (
                    self.raw_limit
                    if expensive
                    else self.grouping_body_limit
                    if scope.get("path") == GROUPING_PATH
                    else JSON_BODY_LIMIT
                )
                declared = self._validate_content_length(scope, request_id, body_limit)
                if scope.get("method") == "DELETE" and declared not in {None, 0}:
                    raise PublicApiError("invalid_content_length", request_id)
                rate_error = self.limiter.begin(client_key)
                if rate_error:
                    raise PublicApiError(rate_error, request_id)
                rate_started = True
                if expensive:
                    if not self.admissions.acquire():
                        raise PublicApiError("verification_capacity_busy", request_id)
                    admitted = True
                    scope["state"]["admission_started"] = started
                limited_receive = self._limited_receive(
                    receive, started, declared, request_id, body_limit
                )
                remaining = max(0.001, self.server_deadline - (time.monotonic() - started))
                await asyncio.wait_for(
                    self.app(scope, limited_receive, secure_send), timeout=remaining
                )
            else:
                await self.app(scope, receive, secure_send)
        except TimeoutError:
            if not response_started:
                await _send_error(
                    PublicApiError("request_deadline_exceeded", request_id), scope, secure_send
                )
        except PublicApiError as exc:
            if not response_started:
                await _send_error(exc, scope, secure_send)
        except Exception:
            if not response_started:
                await _send_error(PublicApiError("internal_error", request_id), scope, secure_send)
            else:
                raise
        finally:
            if admitted:
                self.admissions.release()
            if client_key is not None and rate_started:
                self.limiter.finish(client_key)

    def _validate_host_origin(self, scope: dict[str, Any], request_id: str) -> None:
        if not self.settings.production:
            return
        host_values = _header_values(scope, b"host")
        if len(host_values) != 1:
            raise PublicApiError("invalid_host", request_id)
        try:
            actual = _normalize_host(host_values[0].decode("ascii"))
            expected = _normalize_host(self.settings.allowed_host or "")
        except (UnicodeError, ValueError) as exc:
            raise PublicApiError("invalid_host", request_id) from exc
        if actual != expected:
            raise PublicApiError("invalid_host", request_id)
        if _is_state_change(scope):
            origins = _header_values(scope, b"origin")
            expected_origin = f"https://{expected}".encode("ascii")
            if len(origins) != 1 or origins[0] != expected_origin:
                raise PublicApiError("origin_not_allowed", request_id)

    def _validate_content_length(
        self, scope: dict[str, Any], request_id: str, body_limit: int
    ) -> int | None:
        length_values = _header_values(scope, b"content-length")
        transfer_values = _header_values(scope, b"transfer-encoding")
        if length_values and transfer_values:
            raise PublicApiError("invalid_content_length", request_id)
        if not length_values:
            return None
        if len(length_values) != 1:
            raise PublicApiError("invalid_content_length", request_id)
        raw = length_values[0]
        if not raw or not raw.isdigit():
            raise PublicApiError("invalid_content_length", request_id)
        value = int(raw)
        if value > body_limit:
            raise PublicApiError("request_too_large", request_id)
        return value

    def _limited_receive(
        self,
        receive: Any,
        started: float,
        declared: int | None,
        request_id: str,
        body_limit: int,
    ) -> Any:
        total = 0
        finished = False

        async def wrapped() -> dict[str, Any]:
            nonlocal total, finished
            if finished:
                return {"type": "http.request", "body": b"", "more_body": False}
            remaining = self.upload_deadline - (time.monotonic() - started)
            if remaining <= 0:
                raise PublicApiError("upload_timeout", request_id)
            try:
                message: dict[str, Any] = await asyncio.wait_for(receive(), timeout=remaining)
            except TimeoutError as exc:
                raise PublicApiError("upload_timeout", request_id) from exc
            if message["type"] != "http.request":
                return message
            body = message.get("body", b"")
            total += len(body)
            if total > body_limit:
                raise PublicApiError("request_too_large", request_id)
            if declared is not None and total > declared:
                raise PublicApiError("content_length_mismatch", request_id)
            if not message.get("more_body", False):
                finished = True
                if declared is not None and total != declared:
                    raise PublicApiError("content_length_mismatch", request_id)
            return message

        return wrapped


def _is_expensive(scope: dict[str, Any]) -> bool:
    if scope.get("method") != "POST":
        return False
    path = str(scope.get("path", ""))
    return path in EXPENSIVE_PATHS or HISTORY_PANEL_ADD_PATTERN.fullmatch(path) is not None


def _is_state_change(scope: dict[str, Any]) -> bool:
    method = scope.get("method")
    path = str(scope.get("path", ""))
    return (
        _is_expensive(scope)
        or (method == "POST" and path == GROUPING_PATH)
        or (
            method in {"PATCH", "DELETE"}
            and (path == HISTORY_PATH or path.startswith(f"{HISTORY_PATH}/"))
        )
    )


def _history_scope(scope: dict[str, Any]) -> tuple[str, bool]:
    values = _header_values(scope, b"cookie")
    raw = b"; ".join(values)
    if raw and len(raw) <= 4096:
        try:
            jar = SimpleCookie()
            jar.load(raw.decode("ascii"))
            morsel = jar.get(HISTORY_SCOPE_COOKIE)
            if morsel is not None and HISTORY_SCOPE_PATTERN.fullmatch(morsel.value):
                return morsel.value, False
        except (UnicodeError, ValueError):
            pass
    return secrets.token_urlsafe(32), True


def _scope_cookie(scope_id: str, production: bool) -> bytes:
    attributes = [
        f"{HISTORY_SCOPE_COOKIE}={scope_id}",
        "Path=/",
        f"Max-Age={HISTORY_SCOPE_MAX_AGE}",
        "HttpOnly",
        "SameSite=Strict",
    ]
    if production:
        attributes.append("Secure")
    return "; ".join(attributes).encode("ascii")


async def _send_error(error: PublicApiError, scope: dict[str, Any], send: Any) -> None:
    response = JSONResponse(
        error.public().model_dump(by_alias=True, exclude_none=True), status_code=error.http_status
    )
    await response(scope, _empty_receive, send)


async def _empty_receive() -> dict[str, Any]:
    message: dict[str, Any] = {
        "type": "http.request",
        "body": b"",
        "more_body": False,
    }
    return message


def _security_headers(
    headers: list[tuple[bytes, bytes]], *, production: bool, no_store: bool
) -> list[tuple[bytes, bytes]]:
    controlled = {
        b"x-content-type-options": b"nosniff",
        b"referrer-policy": b"no-referrer",
        b"x-frame-options": b"DENY",
        b"cross-origin-opener-policy": b"same-origin",
        b"permissions-policy": b"camera=(), microphone=(), geolocation=()",
    }
    if no_store:
        controlled[b"cache-control"] = b"no-store, private"
        controlled[b"pragma"] = b"no-cache"
    if production:
        controlled[b"strict-transport-security"] = b"max-age=31536000; includeSubDomains"
    content_types = [value for name, value in headers if name.lower() == b"content-type"]
    if content_types and content_types[0].lower().startswith(b"text/html"):
        controlled[b"content-security-policy"] = (
            b"default-src 'self'; img-src 'self' blob:; connect-src 'self'; "
            b"style-src 'self'; script-src 'self'; object-src 'none'; base-uri 'self'; "
            b"frame-ancestors 'none'; form-action 'self'"
        )
    names = set(controlled)
    retained = [(name, value) for name, value in headers if name.lower() not in names]
    return retained + list(controlled.items())


def _normalize_host(value: str) -> str:
    raw = value.strip().casefold()
    if not raw or any(character in raw for character in " /,@"):
        raise ValueError("Malformed host")
    if raw.startswith("["):
        end = raw.find("]")
        if end < 0:
            raise ValueError("Malformed IPv6 host")
        hostname = raw[: end + 1]
        suffix = raw[end + 1 :]
        port = suffix[1:] if suffix.startswith(":") else ""
        if suffix and not suffix.startswith(":"):
            raise ValueError("Malformed host port")
    else:
        parts = raw.rsplit(":", 1)
        hostname, port = (
            (parts[0], parts[1]) if len(parts) == 2 and parts[1].isdigit() else (raw, "")
        )
    if port and (not port.isdigit() or not 0 < int(port) <= 65535):
        raise ValueError("Malformed host port")
    if not hostname.startswith("["):
        hostname = hostname.encode("idna").decode("ascii")
    return hostname if port in {"", "443"} else f"{hostname}:{port}"
