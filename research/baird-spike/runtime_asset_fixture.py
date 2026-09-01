from __future__ import annotations

import os
import shutil
import stat
import tempfile
from pathlib import Path

import rapidocr


ROOT = Path(__file__).resolve().parent
MODEL_NAMES = (
    "en_PP-OCRv3_det_infer.onnx",
    "en_PP-OCRv4_rec_infer.onnx",
    "ch_ppocr_mobile_v2.0_cls_infer.onnx",
)


class RuntimeAssetFixture:
    def __init__(self, readonly: bool = True):
        self.readonly = readonly
        self.root: Path | None = None

    def __enter__(self):
        asset_parent = Path(os.environ.get("TEMP") or os.environ.get("TMP") or Path.cwd())
        self.root = Path(tempfile.mkdtemp(prefix="baird-assets-", dir=asset_parent))
        model_root = self.root / "models"
        model_root.mkdir()
        source_models = Path(rapidocr.__file__).resolve().parent / "models"
        for name in MODEL_NAMES:
            shutil.copy2(source_models / name, model_root / name)
        shutil.copy2(ROOT / "selected-check-registry.json", self.root / "selected-check-registry.json")
        shutil.copy2(ROOT / "regulatory-rules.json", self.root / "regulatory-rules.json")
        if self.readonly:
            for path in self.root.rglob("*"):
                if path.is_file():
                    path.chmod(stat.S_IREAD)
        return {
            "LABELVERIFY_MODEL_ROOT": str(model_root),
            "LABELVERIFY_CHECK_REGISTRY_PATH": str(self.root / "selected-check-registry.json"),
            "LABELVERIFY_REGULATORY_RULES_PATH": str(self.root / "regulatory-rules.json"),
        }

    def __exit__(self, *_):
        if not self.root:
            return
        for path in self.root.rglob("*"):
            if path.is_file():
                path.chmod(stat.S_IWRITE | stat.S_IREAD)
        shutil.rmtree(self.root, ignore_errors=True)


def environment_with_assets(asset_environment: dict[str, str], **overrides: str) -> dict[str, str]:
    return {**os.environ, **asset_environment, **overrides}
