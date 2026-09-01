from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator
from pathlib import Path
from typing import Any

import pytest
from labelverify.api import multipart as multipart_module
from labelverify.api.multipart import ControlledMultiPartParser
from starlette.datastructures import Headers, UploadFile


def _headers() -> Headers:
    return Headers({"Content-Type": "multipart/form-data; boundary=labelverify-boundary"})


def _prefix() -> bytes:
    return (
        b"--labelverify-boundary\r\n"
        b'Content-Disposition: form-data; name="panels"; filename="label.png"\r\n'
        b"Content-Type: image/png\r\n\r\n"
    )


async def _successful_stream() -> AsyncGenerator[bytes, None]:
    yield _prefix() + (b"x" * (1_048_576 + 1))
    yield b"\r\n--labelverify-boundary--\r\n"


async def _failing_stream(error: BaseException) -> AsyncGenerator[bytes, None]:
    yield _prefix() + (b"x" * (1_048_576 + 1))
    raise error


def _record_factory(monkeypatch: pytest.MonkeyPatch) -> list[Path]:
    actual = multipart_module._open_spooled_file
    directories: list[Path] = []

    def recording_factory(spool_root: Path, max_size: int) -> Any:
        directories.append(spool_root.resolve())
        return actual(spool_root, max_size)

    monkeypatch.setattr(multipart_module, "_open_spooled_file", recording_factory)
    return directories


@pytest.mark.asyncio
async def test_framework_spool_uses_governed_root(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    spool_root = tmp_path / "spool"
    spool_root.mkdir()
    directories = _record_factory(monkeypatch)
    parser = ControlledMultiPartParser(
        _headers(),
        _successful_stream(),
        spool_root=spool_root,
        max_files=6,
        max_fields=1,
        max_part_size=4_194_304,
    )
    form = await parser.parse()
    upload = form["panels"]
    assert isinstance(upload, UploadFile)
    assert directories == [spool_root.resolve()]
    await form.close()
    assert list(spool_root.iterdir()) == []


@pytest.mark.asyncio
@pytest.mark.parametrize("error", [RuntimeError("failed"), asyncio.CancelledError()])
async def test_partial_spool_closes_for_every_exception(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    error: BaseException,
) -> None:
    spool_root = tmp_path / "spool"
    spool_root.mkdir()
    directories = _record_factory(monkeypatch)
    parser = ControlledMultiPartParser(
        _headers(),
        _failing_stream(error),
        spool_root=spool_root,
        max_files=6,
        max_fields=1,
        max_part_size=4_194_304,
    )
    with pytest.raises(type(error)):
        await parser.parse()
    assert directories == [spool_root.resolve()]
    assert parser._files_to_close_on_error
    assert all(temporary.closed for temporary in parser._files_to_close_on_error)
    assert list(spool_root.iterdir()) == []
