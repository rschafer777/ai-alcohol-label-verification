from __future__ import annotations

from pathlib import Path

from starlette.exceptions import HTTPException
from starlette.responses import FileResponse, Response
from starlette.staticfiles import StaticFiles
from starlette.types import Scope


class SpaStaticFiles(StaticFiles):
    """Serve the built UI and fall back to index only for non-API navigation."""

    def __init__(self, directory: Path) -> None:
        super().__init__(directory=str(directory), html=True, check_dir=False)
        self._index = directory / "index.html"

    async def get_response(self, path: str, scope: Scope) -> Response:
        normalized = path.lstrip("/")
        if (
            normalized == "api"
            or normalized.startswith("api/")
            or normalized == "health"
            or normalized.startswith("health/")
        ):
            return Response(status_code=404)
        leaf = Path(normalized).name
        try:
            response = await super().get_response(path, scope)
        except HTTPException as exc:
            if exc.status_code == 404 and "." not in leaf and self._index.is_file():
                return FileResponse(self._index)
            raise
        if response.status_code == 404 and "." not in leaf and self._index.is_file():
            return FileResponse(self._index)
        return response
