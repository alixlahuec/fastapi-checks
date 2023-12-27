from pytest import fixture

from fastapi_checks import models


@fixture
def marked_dependency():
    from fastapi_checks.decorators import mark

    @mark("some_tag", "another_tag")
    def _marked_dependency():  # pragma: no cover
        return True

    return _marked_dependency


@fixture
def handler_with_marked_dependency(marked_dependency):
    from fastapi import Depends

    def _handler_with_marked_dependency(arg1: bool = Depends(marked_dependency)):  # pragma: no cover
        return "some value"

    return _handler_with_marked_dependency


@fixture
def dependency_instance(root_app, route_path, dependency, handler_with_dependency):
    from fastapi.routing import APIRoute

    root_app.get(route_path)(handler_with_dependency)
    api_routes = [r for r in root_app.routes if isinstance(r, APIRoute)]

    return models.Dependency(
        argname="arg1",
        callable=dependency,
        route=api_routes[0],
        origin=models.DependencyOrigin.HANDLER,
    )


@fixture
def marked_dependency_instance(root_app, route_path, marked_dependency, handler_with_marked_dependency):
    from fastapi.routing import APIRoute

    root_app.get(route_path)(handler_with_marked_dependency)
    api_routes = [r for r in root_app.routes if isinstance(r, APIRoute)]

    return models.Dependency(
        argname="arg1",
        callable=marked_dependency,
        route=api_routes[0],
        origin=models.DependencyOrigin.HANDLER,
    )


def test_dependency_humanized(dependency_instance):
    assert dependency_instance.humanized == "_dependency"


def test_dependency_no_mark(dependency_instance):
    dep = dependency_instance
    assert dep.mark is None
    assert dep.tags_exclude_all(tags=["a"]) is True
    assert dep.tags_include_all(tags=["b"]) is False
    assert dep.tags_include(tags=["c"]) is False


def test_dependency_with_mark(marked_dependency_instance):
    dep = marked_dependency_instance
    assert isinstance(dep.mark, models.Mark)
    assert dep.tags_exclude_all(tags=["randtag1"]) is True
    assert dep.tags_exclude_all(tags=["some_tag", "randtag1"]) is False
    assert dep.tags_include_all(tags=["some_tag"]) is True
    assert dep.tags_include_all(tags=["another_tag", "some_tag"]) is True
    assert dep.tags_include(tags=["randtag1"]) is False
    assert dep.tags_include(tags=["randtag1", "some_tag"]) is True
