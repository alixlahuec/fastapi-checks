from typing import Any

from fastapi.routing import APIRoute
from functools import cached_property
from pydantic import BaseModel

from fastapi_checks.models import Dependency, Mark
from fastapi_checks.models.openapi import SecurityScheme
from fastapi_checks.models.utils import SearchRegex, regex_match
from fastapi_checks.parser.api_route import get_dependencies
from fastapi_checks.parser.openapi import (
    get_endpoint_operation_id,
    get_endpoint_security,
)


class ApiRoute(BaseModel):
    route: APIRoute
    openapi: dict[str, Any]

    class Config:
        arbitrary_types_allowed = True
        keep_untouched = (cached_property,)

    def predicate(self, *, path_regex: SearchRegex | None = None) -> bool:
        if path_regex:
            return regex_match(path_regex, self.route.path)
        else:
            return True

    @cached_property
    def dependencies(self) -> list[Dependency]:
        return get_dependencies(self.route)

    @cached_property
    def unique_dependencies(self) -> list[Dependency]:
        uniques: list[Dependency] = []

        for dep in self.dependencies:
            if any(x.callable is dep.callable for x in uniques):
                continue
            else:
                uniques.append(dep)

        return uniques

    @property
    def dependency_names(self) -> list[str]:
        return [dep.humanized for dep in self.unique_dependencies]

    @property
    def dependency_marks(self) -> list[Mark]:
        return [dep.mark for dep in self.unique_dependencies if dep.mark]

    @property
    def operation_id(self) -> str:
        return get_endpoint_operation_id(self.openapi)

    @property
    def security(
        self, scheme: SecurityScheme = SecurityScheme.HTTP_BEARER
    ) -> list[str]:
        return get_endpoint_security(self.openapi, scheme)
