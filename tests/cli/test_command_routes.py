from typer.testing import CliRunner

from fastapi_checks.cli.main import app


runner = CliRunner()


def test_routes_terminal(base_args, dash_run_mock, snapshot):
    res = runner.invoke(app, [*base_args, "routes", "--no-html"])

    assert res.exit_code == 0
    assert res.stdout == snapshot

    dash_run_mock.assert_not_called()


def test_routes_html(base_args, dash_run_mock, rich_print_mock):
    res = runner.invoke(app, [*base_args, "routes", "--html"])

    assert res.exit_code == 0

    dash_run_mock.assert_called_once_with(debug=True)

    rich_print_mock.assert_not_called()
