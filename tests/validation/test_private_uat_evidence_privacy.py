from __future__ import annotations

from pathlib import Path

from scripts.validate_private_uat_corpus_e2e import public_evidence


def test_public_evidence_removes_private_filenames_and_ocr_text(tmp_path: Path) -> None:
    image = tmp_path / "private-person-name.jpg"
    image.write_bytes(b"private test bytes")
    report = {
        "scope": {"skippedFiles": ["private-oracle.json"]},
        "preflightFailures": ["private-person-name.jpg exceeds the limit"],
        "equivalentPanelIntegration": {"files": [image.name]},
        "individualScans": [
            {
                "caseId": "image-001",
                "files": [image.name],
                "observed": {
                    "beverageType": "wine",
                    "brandName": "Private Person",
                    "classType": "Private Class",
                    "producerNameAddress": "Private Home Address",
                    "countryOfOrigin": "Private Country",
                    "detectedFieldCount": 4,
                    "evidenceRegionCount": 5,
                    "machineSummary": "Review needed",
                },
            }
        ],
        "productScans": [
            {
                "caseId": "product-001",
                "files": [image.name],
                "suggestedName": "Private Person",
                "observed": {"brandName": "Private Person"},
            }
        ],
        "grouping": {"groups": [{"suggestedName": "Private Person"}]},
    }

    sanitized = public_evidence(report, tmp_path)
    rendered = str(sanitized)

    assert "private-person-name" not in rendered.casefold()
    assert "private person" not in rendered.casefold()
    assert "private home address" not in rendered.casefold()
    assert sanitized["individualScans"][0]["observed"]["brandRead"] is True
    assert sanitized["individualScans"][0]["fileArtifacts"][0]["sha256"]
    assert sanitized["scope"]["skippedFileExtensions"] == [".json"]
    assert "suggestedName" not in sanitized["grouping"]["groups"][0]
