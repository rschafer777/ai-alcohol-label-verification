from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from labelverify.api.errors import PublicApiError
from labelverify.api.routes import router
from labelverify.api.static import SpaStaticFiles
from labelverify.contracts.loader import contracts
from labelverify.orchestration.supervisor import WorkerSupervisor
from labelverify.security.boundary import BoundaryMiddleware
from labelverify.settings.config import Settings


def create_app(
    *, settings: Settings | None = None, supervisor: WorkerSupervisor | None = None
) -> FastAPI:
    runtime = settings or Settings.from_environment()
    worker = supervisor or WorkerSupervisor(
        runtime.model_root,
        worker_deadline_seconds=float(contracts().api["limits"]["workerDeadlineSeconds"]),
        build_id=runtime.build_id,
    )

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        app.state.settings = runtime
        app.state.supervisor = worker
        runtime.spool_root.mkdir(parents=True, exist_ok=True, mode=0o700)
        await asyncio.to_thread(worker.start)
        try:
            yield
        finally:
            await asyncio.to_thread(worker.stop)

    app = FastAPI(
        title="LabelVerify API",
        version="0.1.0",
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
        lifespan=lifespan,
    )
    app.state.settings = runtime
    app.state.supervisor = worker
    app.include_router(router)

    @app.api_route(
        "/api/{unmatched_path:path}",
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        include_in_schema=False,
    )
    async def unmatched_api(unmatched_path: str) -> JSONResponse:
        del unmatched_path
        return JSONResponse({"detail": "Not Found"}, status_code=404)

    @app.api_route(
        "/health/{unmatched_path:path}",
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        include_in_schema=False,
    )
    async def unmatched_health(unmatched_path: str) -> JSONResponse:
        del unmatched_path
        return JSONResponse({"detail": "Not Found"}, status_code=404)

    @app.exception_handler(PublicApiError)
    async def public_error_handler(_: Request, exc: PublicApiError) -> JSONResponse:
        return JSONResponse(
            exc.public().model_dump(by_alias=True, exclude_none=True), status_code=exc.http_status
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, _: RequestValidationError) -> JSONResponse:
        error = PublicApiError("invalid_reference", request.state.request_id, "reference")
        return JSONResponse(
            error.public().model_dump(by_alias=True, exclude_none=True),
            status_code=error.http_status,
        )

    @app.exception_handler(Exception)
    async def internal_error_handler(request: Request, _: Exception) -> JSONResponse:
        error = PublicApiError("internal_error", request.state.request_id)
        return JSONResponse(
            error.public().model_dump(by_alias=True, exclude_none=True),
            status_code=error.http_status,
        )

    app.add_middleware(BoundaryMiddleware, settings=runtime)
    app.mount("/", SpaStaticFiles(runtime.static_root), name="frontend")
    return app


app: Any = create_app()
