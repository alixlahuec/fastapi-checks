from pytest import fixture, mark

from fastapi_checks.models import DependencyOrigin
from fastapi_checks.parser.callable import get_dependencies, get_dependencies_recursive


@fixture
def l3_dependency():
    class Dep3:
        some_prop = "val"

    return Dep3


@fixture
def l2_dependency(l3_dependency):
    from fastapi import Depends

    def dep2(l3: l3_dependency = Depends()):  # pragma: no cover
        return l3.some_prop  # type: ignore

    return dep2


@fixture
def l1_dependency(l2_dependency):
    from fastapi import Depends

    def dep1(l2=Depends(l2_dependency)):  # pragma: no cover
        return f"deep return: {l2}"

    return dep1


@fixture
def handler_with_chained_deps(l1_dependency):
    from fastapi import Depends

    def _handler_with_chained_deps(l1=Depends(l1_dependency)):  # pragma: no cover
        return f"endpoint - {l1}"

    return _handler_with_chained_deps


@fixture
def api_route(root_app, route_path, handler_with_chained_deps):
    from fastapi.routing import APIRoute

    root_app.get(route_path)(handler_with_chained_deps)

    return [
        r for r in root_app.routes if isinstance(r, APIRoute) and r.path == route_path
    ][0]


@mark.parametrize(
    "callable_fixture, expected_deps_count, expected_recursive_deps_count",
    [
        ("handler_with_chained_deps", 1, 3),
        ("l1_dependency", 1, 2),
        ("l2_dependency", 1, 1),
        ("l3_dependency", 0, 0),
    ],
)
def test_callable_get_dependencies(
    request,
    api_route,
    callable_fixture,
    expected_deps_count,
    expected_recursive_deps_count,
):
    cbl = request.getfixturevalue(callable_fixture)

    assert (
        len(get_dependencies(cbl, route=api_route, origin=DependencyOrigin.HANDLER))
        == expected_deps_count
    )

    assert (
        len(
            get_dependencies_recursive(
                cbl, route=api_route, origin=DependencyOrigin.HANDLER
            )
        )
        == expected_recursive_deps_count
    )
