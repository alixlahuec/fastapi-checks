from fastapi import FastAPI
from pytest import fixture

from fastapi_checks import models


@fixture
def fastapi_app():
    raise Exception(
        "fastapi_app fixture is not defined. Define a fastapi_app fixture that "
        "returns a FastAPI instance to run tests against."
    )


@fixture
def fastapi_checks(fastapi_app: FastAPI) -> models.App:
    return models.App(app=fastapi_app)


FastApiChecks = models.App
