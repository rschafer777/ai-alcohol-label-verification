"""Reference-blind OCR extraction port and candidate location."""

from labelverify.extraction.candidates import locate_candidates
from labelverify.extraction.rapidocr_adapter import RapidOcrAdapter

__all__ = ["RapidOcrAdapter", "locate_candidates"]
