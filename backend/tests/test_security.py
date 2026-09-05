from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest
from labelverify.api.errors import PublicApiError
from labelverify.security.boundary import (
    HISTORY_SCOPE_COOKIE,
    _history_scope,
    _is_state_change,
    _normalize_host,
    _scope_cookie,
    _security_headers,
)
from labelverify.security.identity import ClientIdentity
from labelverify.security.rate_limit import AdmissionController, StartRateLimiter
from labelverify.security.signatures import image_media_type
from labelverify.settings.config import Settings


def settings(tmp_path: Path, *, production: bool = False) -> Settings:
    return Settings(
        runtime_mode="production" if production else "direct",
        allowed_host="verify.example.gov" if production else None,
        model_root=tmp_path / "models",
        spool_root=tmp_path / "spool",
        sample_manifest=tmp_path / "sample.json",
        static_root=tmp_path / "dist",
        build_id="test",
    )


def scope(headers: list[tuple[bytes, bytes]], client: str = "127.0.0.1") -> dict[str, object]:
    return {"headers": headers, "client": (client, 1234)}


def test_production_environment_requires_an_explicit_identity_source(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("LABELVERIFY_RUNTIME_MODE", "production")
    monkeypatch.setenv("LABELVERIFY_ALLOWED_HOST", "verify.example.gov")
    monkeypatch.delenv("LABELVERIFY_CLIENT_IDENTITY_SOURCE", raising=False)
    with pytest.raises(ValueError, match="LABELVERIFY_CLIENT_IDENTITY_SOURCE"):
        Settings.from_environment()

    monkeypatch.setenv("LABELVERIFY_CLIENT_IDENTITY_SOURCE", "azure_container_apps")
    resolved = Settings.from_environment()
    assert resolved.client_identity_source == "azure_container_apps"


@pytest.mark.parametrize(
    ("prefix", "expected"),
    [
        (b"\xff\xd8\xff\xe0", "image/jpeg"),
        (b"\x89PNG\r\n\x1a\n", "image/png"),
        (b"RIFF\x00\x00\x00\x00WEBP", "image/webp"),
        (b"GIF89a", None),
    ],
)
def test_signature_sniff(prefix: bytes, expected: str | None) -> None:
    assert image_media_type(prefix) == expected


def test_direct_identity_ignores_forwarding_headers(tmp_path: Path) -> None:
    resolver = ClientIdentity(secret=b"x" * 32)
    direct = settings(tmp_path)
    first = resolver.resolve(
        scope([(b"fly-client-ip", b"198.51.100.2"), (b"x-forwarded-for", b"203.0.113.8")]),
        direct,
        "request",
    )
    second = resolver.resolve(scope([], client="127.0.0.1"), direct, "request")
    assert first == second
    assert "127.0.0.1" not in first


def test_production_identity_requires_one_valid_fly_ip(tmp_path: Path) -> None:
    resolver = ClientIdentity(secret=b"x" * 32)
    production = settings(tmp_path, production=True)
    digest = resolver.resolve(scope([(b"fly-client-ip", b"2001:db8::1")]), production, "r")
    assert len(digest) == 64
    for value in ([], [(b"fly-client-ip", b"bad")], [(b"fly-client-ip", b"1.1.1.1,2.2.2.2")]):
        with pytest.raises(PublicApiError) as caught:
            resolver.resolve(scope(value), production, "r")
        assert caught.value.code == "invalid_client_identity"


def test_azure_identity_uses_only_the_ingress_appended_rightmost_ip(tmp_path: Path) -> None:
    resolver = ClientIdentity(secret=b"x" * 32)
    azure = replace(
        settings(tmp_path, production=True),
        client_identity_source="azure_container_apps",
    )
    expected = resolver.resolve(scope([(b"x-forwarded-for", b"203.0.113.7")]), azure, "request")
    spoofed_prefix = resolver.resolve(
        scope([(b"x-forwarded-for", b"198.51.100.99, 203.0.113.7")]),
        azure,
        "request",
    )
    assert expected == spoofed_prefix
    assert len(expected) == 64

    rejected = (
        [],
        [(b"x-forwarded-for", b"bad")],
        [(b"x-forwarded-for", b"198.51.100.1,")],
        [(b"x-forwarded-for", b"fe80::1%eth0")],
        [(b"x-forwarded-for", b"203.0.113.7"), (b"x-forwarded-for", b"203.0.113.8")],
    )
    for headers in rejected:
        with pytest.raises(PublicApiError) as caught:
            resolver.resolve(scope(headers), azure, "request")
        assert caught.value.code == "invalid_client_identity"


def test_unknown_production_identity_source_fails_closed(tmp_path: Path) -> None:
    resolver = ClientIdentity(secret=b"x" * 32)
    unknown = replace(settings(tmp_path, production=True), client_identity_source="unknown")
    with pytest.raises(PublicApiError) as caught:
        resolver.resolve(scope([(b"x-forwarded-for", b"203.0.113.7")]), unknown, "request")
    assert caught.value.code == "invalid_client_identity"


def test_rate_limits_and_active_isolation() -> None:
    limiter = StartRateLimiter(
        client_starts_per_ten_minutes=20,
        global_starts_per_minute=30,
    )
    assert limiter.begin("client", now=0) is None
    assert limiter.begin("client", now=1) == "client_rate_limited"
    limiter.finish("client")
    for second in range(1, 20):
        assert limiter.begin("client", now=float(second)) is None
        limiter.finish("client")
    assert limiter.begin("client", now=21) == "client_rate_limited"


def test_one_client_cannot_consume_the_global_minute_allowance() -> None:
    limiter = StartRateLimiter(
        client_starts_per_minute=3,
        client_starts_per_ten_minutes=20,
        global_starts_per_minute=5,
    )
    for second in range(3):
        assert limiter.begin("noisy", now=float(second)) is None
        limiter.finish("noisy")
    assert limiter.begin("noisy", now=3.0) == "client_rate_limited"
    assert limiter.begin("other", now=3.0) is None
    limiter.finish("other")


def test_default_rate_limit_supports_one_sequential_peak_batch() -> None:
    limiter = StartRateLimiter()
    for second in range(300):
        assert limiter.begin("client", now=float(second)) is None
        limiter.finish("client")
    assert limiter.counters.active == 0


def test_admission_reservation_returns_to_zero() -> None:
    controller = AdmissionController()
    assert controller.acquire()
    assert controller.acquire()
    assert not controller.acquire()
    assert controller.counters == (2, 34_603_008)
    controller.release()
    controller.release()
    assert controller.counters == (0, 0)


def test_host_normalization_is_exact_and_safe() -> None:
    assert _normalize_host("Example.COM:443") == "example.com"
    assert _normalize_host("example.com:8443") == "example.com:8443"
    with pytest.raises(ValueError):
        _normalize_host("example.com,evil.example")


def test_security_headers_apply_no_store_and_html_csp() -> None:
    headers = _security_headers(
        [(b"content-type", b"text/html; charset=utf-8")], production=True, no_store=True
    )
    values = dict(headers)
    assert values[b"cache-control"] == b"no-store, private"
    assert values[b"strict-transport-security"].startswith(b"max-age=")
    assert b"default-src 'self'" in values[b"content-security-policy"]


def test_history_scope_cookie_is_opaque_strict_and_secure_in_production() -> None:
    generated, should_set = _history_scope({"headers": []})
    assert should_set
    assert len(generated) == 43
    cookie = _scope_cookie(generated, production=True).decode("ascii")
    assert cookie.startswith(f"{HISTORY_SCOPE_COOKIE}={generated};")
    assert "HttpOnly" in cookie
    assert "SameSite=Strict" in cookie
    assert "Secure" in cookie

    recovered, should_replace = _history_scope(
        {"headers": [(b"cookie", f"{HISTORY_SCOPE_COOKIE}={generated}".encode("ascii"))]}
    )
    assert recovered == generated
    assert not should_replace

    replacement, should_replace = _history_scope(
        {"headers": [(b"cookie", f"{HISTORY_SCOPE_COOKIE}=predictable".encode("ascii"))]}
    )
    assert replacement != "predictable"
    assert should_replace


def test_correction_post_is_a_protected_state_change() -> None:
    assert _is_state_change(
        {
            "method": "POST",
            "path": "/api/v1/history/hist_0123456789abcdef/corrections",
        }
    )
    assert _is_state_change(
        {
            "method": "POST",
            "path": "/api/v1/history/not-a-valid-history-id/corrections",
        }
    )
