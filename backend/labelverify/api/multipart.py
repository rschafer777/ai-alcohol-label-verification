from __future__ import annotations

from collections.abc import AsyncGenerator
from pathlib import Path
from tempfile import SpooledTemporaryFile
from typing import BinaryIO, cast

from python_multipart.multipart import parse_options_header
from starlette.datastructures import FormData, Headers, UploadFile
from starlette.formparsers import MultiPartException, MultiPartParser


def _decode_header(value: bytes, charset: str) -> str:
    try:
        return value.decode(charset)
    except (LookupError, UnicodeDecodeError):
        return value.decode("latin-1")


def _open_spooled_file(spool_root: Path, max_size: int) -> SpooledTemporaryFile[bytes]:
    return SpooledTemporaryFile(  # noqa: SIM115 - ownership transfers to UploadFile
        max_size=max_size,
        mode="w+b",
        dir=str(spool_root),
    )


class ControlledMultiPartParser(MultiPartParser):
    """Keep every multipart spill in the governed spool and close it on every error."""

    def __init__(
        self,
        headers: Headers,
        stream: AsyncGenerator[bytes, None],
        *,
        spool_root: Path,
        max_files: int | float,
        max_fields: int | float,
        max_part_size: int,
    ) -> None:
        self._spool_root = spool_root
        super().__init__(
            headers,
            stream,
            max_files=max_files,
            max_fields=max_fields,
            max_part_size=max_part_size,
        )

    def on_headers_finished(self) -> None:
        _, options = parse_options_header(self._current_part.content_disposition)
        try:
            self._current_part.field_name = _decode_header(options[b"name"], self._charset)
        except KeyError as exc:
            raise MultiPartException(
                'The Content-Disposition header field "name" must be provided.'
            ) from exc
        if b"filename" in options:
            self._current_files += 1
            if self._current_files > self.max_files:
                raise MultiPartException(
                    f"Too many files. Maximum number of files is {self.max_files}."
                )
            filename = _decode_header(options[b"filename"], self._charset)
            temporary = _open_spooled_file(self._spool_root, self.spool_max_size)
            self._files_to_close_on_error.append(temporary)
            self._current_part.file = UploadFile(
                file=cast(BinaryIO, temporary),
                size=0,
                filename=filename,
                headers=Headers(raw=self._current_part.item_headers),
            )
        else:
            self._current_fields += 1
            if self._current_fields > self.max_fields:
                raise MultiPartException(
                    f"Too many fields. Maximum number of fields is {self.max_fields}."
                )
            self._current_part.file = None

    async def parse(self) -> FormData:
        try:
            return await super().parse()
        except BaseException:
            for temporary in self._files_to_close_on_error:
                temporary.close()
            raise
