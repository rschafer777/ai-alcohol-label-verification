from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

from scripts.generate_release_manifest import included_files, staged_file_hashes


def test_public_manifest_excludes_local_controls_and_nonredistributable_images(
    tmp_path: Path,
) -> None:
    output = tmp_path / "docs/10-release/RELEASE_MANIFEST.sha256"
    included = tmp_path / "README.md"
    agent_control = tmp_path / "AGENTS.md"
    raw_image = tmp_path / "tests/Test_Images/example.jpg"
    oracle = tmp_path / "tests/Test_Images/test-oracle-v1.json"
    local_environment = tmp_path / ".env.local"
    environment_example = tmp_path / ".env.example"
    raw_python_coverage = tmp_path / "docs/08-validation/evidence/python-coverage.json"
    raw_frontend_coverage = (
        tmp_path / "docs/08-validation/evidence/frontend-coverage-json/coverage-final.json"
    )

    for path in (
        included,
        agent_control,
        raw_image,
        oracle,
        local_environment,
        environment_example,
        raw_python_coverage,
        raw_frontend_coverage,
    ):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("test\n", encoding="utf-8")

    selected = {path.relative_to(tmp_path).as_posix() for path in included_files(tmp_path, output)}

    assert "README.md" in selected
    assert "tests/Test_Images/test-oracle-v1.json" in selected
    assert ".env.example" in selected
    assert "AGENTS.md" not in selected
    assert ".env.local" not in selected
    assert "docs/08-validation/evidence/python-coverage.json" not in selected
    assert "docs/08-validation/evidence/frontend-coverage-json/coverage-final.json" not in selected
    assert "tests/Test_Images/example.jpg" not in selected

    attributes = tmp_path / ".gitattributes"
    evidence = tmp_path / "evidence.json"
    attributes.write_text("*.json text eol=lf\n", encoding="utf-8")
    evidence.write_bytes(b'{"result":"pass"}\r\n')

    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(
        ["git", "add", ".gitattributes", "evidence.json"],
        cwd=tmp_path,
        check=True,
    )

    entries = dict(staged_file_hashes(tmp_path, output))

    assert entries["evidence.json"] == hashlib.sha256(b'{"result":"pass"}\n').hexdigest()
    assert entries["evidence.json"] != hashlib.sha256(evidence.read_bytes()).hexdigest()
