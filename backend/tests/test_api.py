from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient
from labelverify.api.app import create_app
from labelverify.contracts.models import ReferenceRecord
from labelverify.orchestration.supervisor import SupervisorSnapshot
from labelverify.settings.config import Settings

from .helpers import fake_result, jpeg_bytes, reference


class FakeSupervisor:
    ready = True

    def __init__(self) -> None:
        self.started = False
        self.stopped = False
        self.calls = 0

    def start(self) -> bool:
        self.started = True
        return True

    def stop(self) -> None:
        self.stopped = True

    def snapshot(self) -> SupervisorSnapshot:
        return SupervisorSnapshot(True, 1, 0, 0, 0, 123)

    def run(
        self, request_id: str, reference_value: ReferenceRecord, paths: tuple[Path, ...]
    ) -> object:
        self.calls += 1
        assert reference_value.brand_name
        assert len(paths) == 1
        assert paths[0].is_file()
        return fake_result(request_id)


def runtime(
    tmp_path: Path,
    *,
    production: bool = False,
    client_identity_source: str = "fly",
) -> Settings:
    sample_root = tmp_path / "fixtures" / "sample"
    panel_root = sample_root / "panels"
    panel_root.mkdir(parents=True)
    panel_bytes = jpeg_bytes()
    (panel_root / "panel-1.jpg").write_bytes(panel_bytes)
    sample = sample_root / "sample-manifest-v1.json"
    sample.write_text(
        json.dumps(
            {
                "sampleId": "distilled-spirits-v1",
                "contractHashes": {"api-contract-v1.json": "accepted-hash"},
                "reference": reference().model_dump(by_alias=True, mode="json"),
                "panels": [
                    {
                        "panelId": "panel-1",
                        "path": "fixtures/sample/panels/panel-1.jpg",
                        "mimeType": "image/jpeg",
                        "sha256": "accepted-panel-hash",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    static_root = tmp_path / "dist"
    static_root.mkdir()
    (static_root / "index.html").write_text(
        "<!doctype html><title>LabelVerify</title><div id='root'></div>", encoding="utf-8"
    )
    (static_root / "asset.js").write_text("window.labelVerify=true", encoding="utf-8")
    return Settings(
        runtime_mode="production" if production else "direct",
        allowed_host="verify.example.gov" if production else None,
        model_root=tmp_path / "models",
        spool_root=tmp_path / "spool",
        sample_manifest=sample,
        static_root=static_root,
        build_id="test-build",
        client_identity_source=client_identity_source,
    )


def multipart_reference() -> str:
    return reference().model_dump_json(by_alias=True)


def test_health_meta_sample_static_and_spa_same_origin(tmp_path: Path) -> None:
    supervisor = FakeSupervisor()
    app = create_app(settings=runtime(tmp_path), supervisor=supervisor)  # type: ignore[arg-type]
    with TestClient(app, client=("127.0.0.1", 50000)) as client:
        assert client.get("/health/live").json() == {"live": True}
        ready = client.get("/health/ready")
        assert ready.status_code == 200
        meta = client.get("/api/v1/meta").json()
        assert meta["selectedCheckCount"] == 19
        assert "model_root" not in json.dumps(meta).casefold()
        sample_response = client.get("/api/v1/samples/distilled-spirits-v1")
        assert sample_response.status_code == 200
        sample_body = sample_response.json()
        assert sample_body["contractHashes"]["api-contract-v1.json"] == "accepted-hash"
        assert sample_body["panels"] == [
            {
                "panelId": "panel-1",
                "mimeType": "image/jpeg",
                "sha256": "accepted-panel-hash",
                "label": "Front label",
                "fileName": "panel-1.jpg",
                "url": "/api/v1/samples/distilled-spirits-v1/panels/panel-1",
            }
        ]
        panel_response = client.get(sample_body["panels"][0]["url"])
        assert panel_response.status_code == 200
        assert panel_response.content == jpeg_bytes()
        assert panel_response.headers["content-type"] == "image/jpeg"
        assert client.get("/api/v1/samples/distilled-spirits-v1/panels/panel-2").status_code == 503
        index = client.get("/")
        assert index.status_code == 200
        assert "LabelVerify" in index.text
        assert "default-src 'self'" in index.headers["content-security-policy"]
        assert client.get("/review/evidence").status_code == 200
        assert client.get("/asset.js").status_code == 200
        assert client.get("/api/v1/unknown").status_code == 404
    assert supervisor.started and supervisor.stopped


def test_valid_verification_is_complete_no_store_and_cleans_spool(tmp_path: Path) -> None:
    supervisor = FakeSupervisor()
    settings = runtime(tmp_path)
    app = create_app(settings=settings, supervisor=supervisor)  # type: ignore[arg-type]
    with TestClient(app, client=("127.0.0.1", 50000)) as client:
        response = client.post(
            "/api/v1/verifications",
            data={"reference": multipart_reference()},
            files={"panels": ("private-name.jpg", jpeg_bytes(), "image/jpeg")},
        )
    assert response.status_code == 200, response.text
    body = response.json()
    assert len(body["checks"]) == 19
    assert body["panels"][0]["originalDimensions"] == {"width": 640, "height": 900}
    assert "originalWidth" not in body["panels"][0]
    assert "originalHeight" not in body["panels"][0]
    assert response.headers["cache-control"] == "no-store, private"
    assert supervisor.calls == 1
    assert list(settings.spool_root.iterdir()) == []


def test_invalid_reference_is_result_free_and_does_not_run_worker(tmp_path: Path) -> None:
    supervisor = FakeSupervisor()
    app = create_app(settings=runtime(tmp_path), supervisor=supervisor)  # type: ignore[arg-type]
    with TestClient(app, client=("127.0.0.1", 50000)) as client:
        response = client.post(
            "/api/v1/verifications",
            data={"reference": "{}"},
            files={"panels": ("label.jpg", jpeg_bytes(), "image/jpeg")},
        )
    assert response.status_code == 422
    assert response.json()["code"] == "invalid_reference"
    assert "checks" not in response.json()
    assert supervisor.calls == 0


def test_signature_not_extension_controls_media_type(tmp_path: Path) -> None:
    supervisor = FakeSupervisor()
    app = create_app(settings=runtime(tmp_path), supervisor=supervisor)  # type: ignore[arg-type]
    with TestClient(app, client=("127.0.0.1", 50000)) as client:
        response = client.post(
            "/api/v1/verifications",
            data={"reference": multipart_reference()},
            files={"panels": ("looks-valid.jpg", b"not an image", "image/jpeg")},
        )
    assert response.status_code == 415
    assert response.json()["fieldOrPanel"] == "panel-1"
    assert supervisor.calls == 0


def test_production_edge_requires_exact_identity_host_and_origin(tmp_path: Path) -> None:
    supervisor = FakeSupervisor()
    app = create_app(
        settings=runtime(tmp_path, production=True),
        supervisor=supervisor,  # type: ignore[arg-type]
    )
    files = {"panels": ("label.jpg", jpeg_bytes(), "image/jpeg")}
    with TestClient(
        app, client=("127.0.0.1", 50000), base_url="https://verify.example.gov"
    ) as client:
        missing_identity = client.post(
            "/api/v1/verifications",
            headers={"Origin": "https://verify.example.gov"},
            data={"reference": multipart_reference()},
            files=files,
        )
        assert missing_identity.status_code == 400
        assert missing_identity.json()["code"] == "invalid_client_identity"
        valid = client.post(
            "/api/v1/verifications",
            headers={
                "Origin": "https://verify.example.gov",
                "Fly-Client-IP": "203.0.113.7",
            },
            data={"reference": multipart_reference()},
            files=files,
        )
        assert valid.status_code == 200, valid.text
        assert valid.headers["strict-transport-security"].startswith("max-age=")


def test_azure_production_edge_accepts_only_its_trusted_identity_chain(tmp_path: Path) -> None:
    supervisor = FakeSupervisor()
    app = create_app(
        settings=runtime(
            tmp_path,
            production=True,
            client_identity_source="azure_container_apps",
        ),
        supervisor=supervisor,  # type: ignore[arg-type]
    )
    files = {"panels": ("label.jpg", jpeg_bytes(), "image/jpeg")}
    with TestClient(
        app, client=("127.0.0.1", 50000), base_url="https://verify.example.gov"
    ) as client:
        fly_only = client.post(
            "/api/v1/verifications",
            headers={
                "Origin": "https://verify.example.gov",
                "Fly-Client-IP": "203.0.113.7",
            },
            data={"reference": multipart_reference()},
            files=files,
        )
        assert fly_only.status_code == 400
        assert fly_only.json()["code"] == "invalid_client_identity"

        valid = client.post(
            "/api/v1/verifications",
            headers={
                "Origin": "https://verify.example.gov",
                "X-Forwarded-For": "198.51.100.99, 203.0.113.7",
            },
            data={"reference": multipart_reference()},
            files=files,
        )
        assert valid.status_code == 200, valid.text
        assert valid.headers["strict-transport-security"].startswith("max-age=")


def test_missing_ready_worker_rejects_before_multipart(tmp_path: Path) -> None:
    supervisor = FakeSupervisor()
    supervisor.ready = False
    app = create_app(settings=runtime(tmp_path), supervisor=supervisor)  # type: ignore[arg-type]
    with TestClient(app, client=("127.0.0.1", 50000)) as client:
        response = client.post(
            "/api/v1/verifications",
            data={"reference": multipart_reference()},
            files={"panels": ("label.jpg", jpeg_bytes(), "image/jpeg")},
        )
    assert response.status_code == 503
    assert response.json()["code"] == "not_ready"
    assert supervisor.calls == 0
