from pytest import fixture, mark

from fastapi_checks import models


@fixture
def operation_id():
    return "some_operation_id"


@fixture
def handler_with_duplicate_dependency(dependency):
    from fastapi import Depends

    def _handler_with_duplicate_dependency(
        arg1=Depends(dependency),
        arg2=Depends(dependency),
    ):  # pragma: no cover
        return "OK"

    return _handler_with_duplicate_dependency


@fixture
def api_route_instance(request, root_app, route_path, operation_id):
    from fastapi.routing import APIRoute

    def _factory(handler_fixture: str):
        handler = request.getfixturevalue(handler_fixture)
        root_app.get(route_path, operation_id=operation_id)(handler)

        api_route = [r for r in root_app.routes if isinstance(r, APIRoute)][0]
        assert api_route.path == route_path

        openapi_spec = root_app.openapi()["paths"][route_path]["get"]

        return models.ApiRoute(
            route=api_route,
            openapi=openapi_spec,
        )

    return _factory


def test_api_route_predicate(api_route_instance, route_path):
    route = api_route_instance("handler_with_dependency")

    assert route.predicate() is True
    assert route.predicate(path_regex=route_path) is True
    assert route.predicate(path_regex="otherpath") is False


@mark.parametrize(
    "handler_fixture, expected_deps_count, expected_unique_deps_count",
    [
        ("path_handler", 0, 0),
        ("handler_with_dependency", 1, 1),
        ("handler_with_duplicate_dependency", 2, 1),
    ],
)
def test_api_route_unique_dependencies(
    api_route_instance, handler_fixture, expected_deps_count, expected_unique_deps_count
):
    route = api_route_instance(handler_fixture)

    assert len(route.dependencies) == expected_deps_count
    assert len(route.unique_dependencies) == expected_unique_deps_count


def test_api_route_properties(api_route_instance, dependency, operation_id):
    route = api_route_instance("handler_with_dependency")

    assert len(route.dependencies) == 1
    assert isinstance(route.dependencies[0], models.Dependency)
    assert route.dependencies == route.unique_dependencies

    assert route.dependency_names == [dependency.__name__]
    assert route.dependency_marks == []
    assert route.operation_id == operation_id
    assert route.security == []
