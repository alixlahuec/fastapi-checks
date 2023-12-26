from fastapi import APIRouter, FastAPI
from pytest import fixture

from fastapi_checks import models
from fastapi_checks.parser.app import get_api_routes


@fixture
def api_router():
    return APIRouter(prefix="/v1")


@fixture
def child_app(path_handler):
    app = FastAPI(title="Child app")
    app.get("")(path_handler)

    return app


def test_get_api_routes_root(root_app, path_handler):
    root_app.get("")(path_handler)

    api_routes = get_api_routes(root_app)
    assert len(api_routes) == 1
    assert isinstance(api_routes[0], models.ApiRoute)


def test_get_api_routes_excludes_websockets(root_app, path_handler):
    root_app.websocket("")(path_handler)

    assert len(get_api_routes(root_app)) == 0


def test_get_api_routes_from_mounted_router(root_app, api_router, path_handler):
    api_router.get("")(path_handler)
    root_app.include_router(api_router)

    assert len(get_api_routes(root_app)) == 1


def test_get_api_routes_excludes_mounted_app(root_app, child_app):
    root_app.mount("/0.1", child_app)

    assert len(get_api_routes(root_app)) == 0
    assert len(get_api_routes(child_app)) == 1
