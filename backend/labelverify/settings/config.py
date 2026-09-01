from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    runtime_mode: str
    allowed_host: str | None
    model_root: Path
    spool_root: Path
    sample_manifest: Path
    static_root: Path
    build_id: str

    @property
    def production(self) -> bool:
        return self.runtime_mode == "production"

    @classmethod
    def from_environment(cls) -> Settings:
        root = Path(__file__).resolve().parents[3]
        mode = os.environ.get("LABELVERIFY_RUNTIME_MODE", "direct").strip().casefold()
        if mode not in {"direct", "production"}:
            raise ValueError("LABELVERIFY_RUNTIME_MODE must be direct or production")
        allowed_host = os.environ.get("LABELVERIFY_ALLOWED_HOST")
        if mode == "production" and not allowed_host:
            raise ValueError("LABELVERIFY_ALLOWED_HOST is required in production")
        return cls(
            runtime_mode=mode,
            allowed_host=allowed_host,
            model_root=Path(
                os.environ.get(
                    "LABELVERIFY_MODEL_ROOT",
                    "/app/models" if mode == "production" else str(root / "models"),
                )
            ),
            spool_root=Path(
                os.environ.get(
                    "LABELVERIFY_SPOOL_ROOT",
                    str(Path(tempfile.gettempdir()) / "labelverify-spool"),
                )
            ),
            sample_manifest=Path(
                os.environ.get(
                    "LABELVERIFY_SAMPLE_MANIFEST",
                    str(root / "fixtures" / "sample" / "sample-manifest-v1.json"),
                )
            ),
            static_root=Path(
                os.environ.get("LABELVERIFY_STATIC_ROOT", str(root / "frontend" / "dist"))
            ),
            build_id=os.environ.get("LABELVERIFY_BUILD_ID", "development"),
        )
