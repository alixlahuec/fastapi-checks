from typing import Annotated, Optional, cast

import rich
from rich.console import Group
from typer import Context, Exit, Typer, Option

from fastapi_checks.models import Globals
from fastapi_checks.cli.dash import run_dash
from fastapi_checks.models.table import Column, Table


def list_routes(
    ctx: Context,
    html: Annotated[
        bool, Option(is_flag=True, help="Render in the browser (uses Dash)")
    ] = False,
    match: Annotated[Optional[str], Option(help="Filter path using a RegExp")] = None,
):
    """List all API routes."""
    app = cast(Globals, ctx.obj).app

    routes = app.api_routes(path_regex=match)

    table = Table(
        columns=[
            Column(
                label="Route",
                width="15%",
                sort="asc",
                rich_theme="yellow",
                style_data={"fontFamily": "monospace", "color": "gold"},
            ),
            Column(
                label="Method",
                width="8%",
                align_data="center",
                rich_theme="cyan",
                style_data={"fontFamily": "monospace", "color": "cyan"},
            ),
            Column(label="Description", width="20%", align_data="center"),
            Column(label="Dependencies", width="10%"),
            Column(label="Dependency marks", width="30%", align_data="center"),
            Column(label="Security", width="15%"),
        ],
    )

    def row_path(r):
        return r.route.path

    def row_method(r):
        return ", ".join(list(r.route.methods))

    def row_description(r):
        return f"{r.route.description or r.route.name} - {r.operation_id}"

    def row_dependencies(r):
        dep_names = [dep.humanized for dep in r.unique_dependencies]
        return ", ".join(dep_names) if html else Group(*dep_names)

    def row_dependency_marks(r):
        marks = [el for mark in r.dependency_marks for el in list(mark.tags)]

        return " - ".join(marks) if html else Group(*marks)

    def row_security(r):
        return " - ".join(r.security)

    # Fill the table rows
    for r in routes:
        table.add_row(
            row_path(r),
            row_method(r),
            row_description(r),
            row_dependencies(r),
            row_dependency_marks(r),
            row_security(r),
        )

    # Render the table
    if html:
        with run_dash(title=f"{app.app.title} - API Routes") as render:
            render(table.html())
    else:
        rich.print(table.rich())

        raise Exit()


cli = Typer(callback=list_routes, invoke_without_command=True)

if __name__ == "__main__":  # pragma: no cover
    cli()
