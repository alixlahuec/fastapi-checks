from pytest import fixture

from fastapi import FastAPI


@fixture
def root_app():
    app = FastAPI(title="Root app")
    return app


@fixture
def app_example() -> FastAPI:
    from app_example.main import app

    return app


@fixture
def route_path():
    return "/path/to/resource"


@fixture
def path_handler():
    def _path_handler():  # pragma: no cover
        return "OK"

    return _path_handler


@fixture
def dependency():
    def _dependency():  # pragma: no cover
        return True

    return _dependency


@fixture
def handler_with_dependency(dependency):
    from fastapi import Depends

    def _handler_with_dependency(arg1: bool = Depends(dependency)):  # pragma: no cover
        return "some value"

    return _handler_with_dependency
