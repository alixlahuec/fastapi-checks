from typer.testing import CliRunner

from fastapi_checks.cli.main import app


runner = CliRunner()


def test_command_help(base_args, snapshot):
    res = runner.invoke(app, [*base_args, "--help"])

    assert res.exit_code == 0
    assert res.stdout == snapshot
