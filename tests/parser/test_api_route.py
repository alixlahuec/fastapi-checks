from fastapi import Depends
from pytest import fixture, mark


@fixture
def class_dependency():
    class ClassDep:
        some_property = "some property value"

    return ClassDep


@fixture
def class_dependency_with_params():
    class ClassDepWithParams:
        def __init__(self, some_param: int):
            self.some_param = some_param

        def __call__(self):  # pragma: no cover
            return self.some_param * 2

    return ClassDepWithParams


@fixture
def handler_with_annotated_dependency(dependency):
    from typing import Annotated

    AnnotatedDep = Annotated[bool, Depends(dependency)]

    def _handler_with_annotated_dependency(
        my_annotated_dep: AnnotatedDep,
    ):  # pragma: no cover
        return "OK"

    return _handler_with_annotated_dependency


@fixture
def handler_with_annotated_class_dependency(class_dependency):
    from typing import Annotated

    AnnotatedClassDep = Annotated[class_dependency, Depends(class_dependency)]

    def _handler_with_annotated_class_dependency(
        my_annotated_class_dep: AnnotatedClassDep,
    ):  # pragma: no cover
        return str(my_annotated_class_dep)

    return _handler_with_annotated_class_dependency


@fixture
def handler_with_annotated_class_dependency_shortcut(class_dependency):
    from typing import Annotated

    AnnotatedClassDep = Annotated[class_dependency, Depends()]

    def _handler_with_annotated_class_dependency_shortcut(
        my_annotated_class_dep: AnnotatedClassDep,
    ):  # pragma: no cover
        return str(my_annotated_class_dep)

    return _handler_with_annotated_class_dependency_shortcut


@fixture
def handler_with_class_dependency(class_dependency):
    from fastapi import Depends

    def _handler_with_class_dependency(
        my_class_dep: class_dependency = Depends(class_dependency),
    ):  # pragma: no cover
        return "OK"

    return _handler_with_class_dependency


@fixture
def handler_with_class_dependency_shortcut(class_dependency):
    from fastapi import Depends

    def _handler_with_class_dependency_shortcut(
        my_class_dep: class_dependency = Depends(),
    ):  # pragma: no cover
        return "OK"

    return _handler_with_class_dependency_shortcut


@fixture
def handler_with_class_dependency_with_params(class_dependency_with_params):
    from fastapi import Depends

    def _handler_with_class_dependency_with_params(
        my_class_dep_with_params: int = Depends(class_dependency_with_params(123)),
    ):  # pragma: no cover
        return my_class_dep_with_params

    return _handler_with_class_dependency_with_params


@fixture
def handler_with_annotated_class_dependency_with_params(class_dependency_with_params):
    from typing import Annotated
    from fastapi import Depends

    AnnotatedClassDepWithParams = Annotated[
        int, Depends(class_dependency_with_params(123))
    ]

    def _handler_with_annotated_class_dependency_with_params(
        my_annotated_class_dep_with_params: AnnotatedClassDepWithParams,
    ):  # pragma: no cover
        return my_annotated_class_dep_with_params

    return _handler_with_annotated_class_dependency_with_params


@mark.parametrize(
    "handler_fixture_name, expected_dependencies_count",
    [
        ("path_handler", 0),
        ("handler_with_dependency", 1),
        ("handler_with_annotated_dependency", 1),
        ("handler_with_class_dependency", 1),
        ("handler_with_class_dependency_shortcut", 1),
        ("handler_with_class_dependency_with_params", 1),
        ("handler_with_annotated_class_dependency", 1),
        ("handler_with_annotated_class_dependency_shortcut", 1),
        ("handler_with_annotated_class_dependency_with_params", 1),
    ],
)
def test_get_dependencies(
    root_app,
    route_path,
    request,
    handler_fixture_name,
    expected_dependencies_count,
):
    from fastapi.routing import APIRoute
    from fastapi_checks.parser.api_route import get_dependencies

    handler = request.getfixturevalue(handler_fixture_name)
    root_app.get(route_path)(handler)

    route = [
        r for r in root_app.routes if isinstance(r, APIRoute) and r.path == route_path
    ][0]

    assert len(get_dependencies(route)) == expected_dependencies_count
