from inspect import signature
from typing import Annotated, Callable, get_args, get_origin

from fastapi import params
from fastapi.routing import APIRoute

from fastapi_checks.models import Dependency, DependencyOrigin


def get_dependencies_recursive(
    cbl: Callable, route: APIRoute, origin: DependencyOrigin
) -> list[Dependency]:
    root_deps = get_dependencies(cbl, route=route, origin=origin)
    subdeps: list[Dependency] = []

    for dep in root_deps:
        subdeps.extend(
            get_dependencies_recursive(dep.callable, route=route, origin=origin)
        )

    return [*root_deps, *subdeps]


def get_dependencies(
    cbl: Callable, *, route: APIRoute, origin: DependencyOrigin
) -> list[Dependency]:
    sig = signature(cbl)

    args_deps = []
    annotated_deps = []

    for name, param in sig.parameters.items():
        # Args/Kwargs dependencies
        # E.g. (some_arg = Depends(some_dependency))
        if isinstance(param.default, params.Depends):
            args_deps.append(
                Dependency(
                    argname=name,
                    callable=param.default.dependency,  # type: ignore
                    route=route,
                    origin=origin,
                )
            )
        # Annotated dependencies
        # E.g. (arg1: Annotated[bool, some_dependency])
        elif get_origin(param.annotation) is Annotated:
            _, maybe_depends = get_args(param.annotation)
            if isinstance(maybe_depends, params.Depends):
                annotated_deps.append(
                    Dependency(
                        argname=name,
                        callable=maybe_depends.dependency,  # type: ignore
                        route=route,
                        origin=origin,
                    )
                )

    return [
        *args_deps,
        *annotated_deps,
    ]
