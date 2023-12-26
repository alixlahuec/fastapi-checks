from enum import Enum
from typing import Any, Callable, Iterable

from fastapi.routing import APIRoute
from pydantic import BaseModel, Field

from fastapi_checks.decorators.mark import MARK_METADATA_KEY
from fastapi_checks.models import Mark


class DependencyOrigin(str, Enum):
    PATH = "path"
    HANDLER = "handler"


class Dependency(BaseModel):
    argname: str | None = None
    callable_: Callable[..., Any] = Field(..., alias="callable")
    route: APIRoute
    origin: DependencyOrigin

    class Config:
        arbitrary_types_allowed = True

    @property
    def callable(self) -> Callable[..., Any]:
        return self.callable_

    @property
    def humanized(self) -> str:
        name = getattr(self.callable, "__name__", None)
        if name:
            return name

        base_class = getattr(self.callable, "__class__", None)
        if base_class:
            return base_class.__name__

        return self.callable.__repr__()  # pragma: no cover

    @property
    def mark(self) -> Mark | None:
        return getattr(self.callable, MARK_METADATA_KEY, None)
    
    def tags_include_all(self, *, tags: Iterable[str] = {}) -> bool:
        return self.mark.predicate(tags_include_all=tags)
    
    def tags_exclude_all(self, *, tags: Iterable[str] = {}) -> bool:
        return self.mark.predicate(tags_exclude_all=tags)
    
    def tags_include(self, *, tags: Iterable[str] = {}) -> bool:
        return self.mark.predicate(tags_include=tags)
