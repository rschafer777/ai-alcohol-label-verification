"""Run the complete local gate and retain a repository-neutral transcript."""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "08-validation" / "evidence" / "local-root-check.txt"


def sanitize(value: str) -> str:
    normalized = value.replace(str(ROOT), "<PROJECT_ROOT>")
    normalized = normalized.replace(str(ROOT).replace("\\", "/"), "<PROJECT_ROOT>")
    return re.sub(r"\x1b\[[0-9;]*m", "", normalized)


def main() -> int:
    environment = os.environ.copy()
    environment.pop("FORCE_COLOR", None)
    environment["NO_COLOR"] = "1"
    completed = subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            "scripts/check.ps1",
        ],
        cwd=ROOT,
        env=environment,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    transcript = sanitize(completed.stdout + completed.stderr)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(transcript, encoding="utf-8")
    print(f"Root gate exit code: {completed.returncode}")
    print(f"Retained gate transcript: {OUTPUT.relative_to(ROOT).as_posix()}")
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
