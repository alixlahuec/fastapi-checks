from typer import Typer

from fastapi_checks.cli.commands import debug, routes
from fastapi_checks.cli.config import setup


app = Typer(
    name="fastapi_checks",
    callback=setup,
)

app.add_typer(debug.cli, name="debug")
app.add_typer(routes.cli, name="routes")


if __name__ == "__main__":  # pragma: no cover
    app()
