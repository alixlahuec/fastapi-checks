from pytest import fixture
from unittest.mock import patch


@fixture(scope="session")
def base_args():
    return ["--app", "app_example.main:app"]


@fixture
def rich_print_mock():
    with patch("rich.console.Console.print") as mock:
        yield mock


@fixture
def dash_run_mock():
    with patch("dash.Dash.run") as mock:
        yield mock
