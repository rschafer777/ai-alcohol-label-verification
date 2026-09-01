"""FastAPI application surface."""

from typing import Any

__all__ = ["create_app"]


def __getattr__(name: str) -> Any:
    if name == "create_app":
        from labelverify.api.app import create_app

        return create_app
    raise AttributeError(name)
