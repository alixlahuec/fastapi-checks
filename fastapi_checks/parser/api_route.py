from fastapi.routing import APIRoute

from fastapi_checks.models import Dependency, DependencyOrigin
from fastapi_checks.parser.callable import get_dependencies_recursive


def get_dependencies(route: APIRoute) -> list[Dependency]:
    path_deps = []

    for depends in route.dependencies:
        path_deps.append(
            Dependency(
                callable=depends.dependency,  # type: ignore
                route=route,
                origin=DependencyOrigin.PATH,
            )
        )

        # Get subdependencies
        path_deps.extend(
            get_dependencies_recursive(
                depends.dependency,  # type: ignore
                route=route,
                origin=DependencyOrigin.PATH,
            )
        )

    handler_deps = get_dependencies_recursive(
        route.endpoint, route=route, origin=DependencyOrigin.HANDLER
    )

    return [
        *path_deps,
        *handler_deps,
    ]
