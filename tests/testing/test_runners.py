import re

from pytest import fixture, mark

from app_example.main import app
from fastapi_checks.testing import FastApiChecks


FAC = FastApiChecks(app=app)


@fixture
def fastapi_app():
    return app


def test_plugin_modes(app_example, fastapi_checks):
    from fastapi_checks.models import App

    assert isinstance(FAC, App)
    assert isinstance(fastapi_checks, App)
    assert FAC.app == fastapi_checks.app == app_example


@mark.parametrize(
    "api_route",
    FAC.api_routes(path_regex=re.compile("0.1")),
)
def test_01_routes_have_security(api_route):
    assert len(api_route.security) > 0


def test_01_routes_have_security_from_fixture(fastapi_checks):
    routes = fastapi_checks.api_routes(path_regex="0.1")

    for r in routes:
        assert len(r.security) > 0


def test_unique_operation_ids(fastapi_checks):
    ids = [r.operation_id for r in fastapi_checks.api_routes()]
    ids_set = set(ids)

    assert len(ids_set) == len(ids)
