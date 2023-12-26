from fastapi import FastAPI
from functools import cached_property
from pydantic import BaseModel
from rich.console import Console, ConsoleOptions, RenderResult

from fastapi_checks.models import ApiRoute, Dependency
from fastapi_checks.models.utils import SearchRegex
from fastapi_checks.parser.app import get_api_routes


class App(BaseModel):
    app: FastAPI

    class Config:
        arbitrary_types_allowed = True
        keep_untouched = (cached_property,)

    @cached_property
    def _all_api_routes(self) -> list[ApiRoute]:
        return get_api_routes(self.app)

    def api_routes(self, *, path_regex: SearchRegex | None = None) -> list[ApiRoute]:
        return [
            route
            for route in self._all_api_routes
            if route.predicate(path_regex=path_regex)
        ]

    def dependencies(
        self, *, path_regex: SearchRegex | None = None
    ) -> dict[str, list[Dependency]]:
        return {
            route.route.path: route.dependencies
            for route in self._all_api_routes
            if route.predicate(path_regex=path_regex)
        }

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        yield f"{self.app.title}{' - ' + self.app.description if self.app.description else ''} ({self.app.version})"
