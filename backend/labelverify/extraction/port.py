from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

from labelverify.contracts.models import OcrLine
from labelverify.imaging.transforms import ImageView


class ExtractionPort(Protocol):
    @property
    def model_identity(self) -> str: ...

    def initialize(self) -> None: ...

    def extract(self, views: Sequence[ImageView]) -> list[OcrLine]: ...
