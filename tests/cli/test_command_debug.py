from typer.testing import CliRunner

from fastapi_checks.cli.main import app


runner = CliRunner()


def test_command_debug(base_args, app_example, snapshot):
    res = runner.invoke(app, [*base_args, "debug"])

    assert res.exit_code == 0
    assert res.stdout == snapshot
