from pycosmiconfig import CosmiconfigResult
from pytest import fixture, mark, raises
from unittest.mock import patch

from fastapi_checks.cli.config import load_config, parse_entrypoint
from fastapi_checks import models


@fixture
def ctx_mock():
    with patch("typer.Context", autospec=True) as mock:
        yield mock


def test_load_config_no_config_file(capsys, ctx_mock):
    with patch("fastapi_checks.cli.config.explorer.search", return_value=None):
        res = load_config(None, ctx_mock)

        assert res is None
        assert (
            "No config file provided, could not autodetect" in capsys.readouterr().out
        )


def test_load_config_with_autodetected_file(ctx_mock):
    path = "some_config_file.toml"
    search_res = CosmiconfigResult(config=dict(), filepath=path)

    with patch(
        "fastapi_checks.cli.config.explorer.search", return_value=search_res
    ), patch("fastapi_checks.cli.config.explorer.load", return_value=search_res):
        res = load_config(None, ctx_mock)

        assert res == path


def test_load_config_with_passed_valid_file(ctx_mock):
    path_to_valid = "tests/cli/fixtures/valid_config.json"

    assert load_config(path_to_valid, ctx_mock) == path_to_valid


def test_load_config_raises_with_empty_config_file(ctx_mock):
    path_to_empty = "tests/cli/fixtures/empty_config.json"

    with raises(Exception) as exc:
        load_config(path_to_empty, ctx_mock)

    assert f"Config from {path_to_empty} is empty" in exc.exconly()


def test_load_config_raises_with_nonexistent_file(ctx_mock):
    path_to_nothing = "tests/cli/fixtures/nonexistentconfig.toml"

    with raises(FileNotFoundError):
        load_config(path_to_nothing, ctx_mock)


@mark.parametrize(
    "entrypoint",
    [".", "module_name", "module_name.export"],
)
def test_parse_entrypoint_raises_with_unrecognized_input(entrypoint):
    with raises(Exception) as exc:
        parse_entrypoint(entrypoint)

    assert "Location provided is not a FastAPI instance" in exc.exconly()


@mark.parametrize(
    "entrypoint",
    ["app_test.main:app"],
)
def test_parse_entrypoint_raises_with_unlocalizable_entrypoint(entrypoint):
    with raises(ModuleNotFoundError):
        parse_entrypoint(entrypoint)


def test_setup(ctx_mock, root_app):
    from fastapi_checks.cli.config import setup

    app = models.App(app=root_app)
    config = None

    setup(ctx_mock, app=app, config=config)

    assert isinstance(ctx_mock.obj, models.Globals)
    assert ctx_mock.obj.app == app
    assert ctx_mock.obj.config == config
