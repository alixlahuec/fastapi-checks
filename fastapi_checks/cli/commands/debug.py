import json
import os
from typing import cast

import rich
from rich.console import Group
from rich.json import JSON
from rich.panel import Panel
from typer import Context, Typer

from fastapi_checks.models import Globals


def show_debug_info(
    ctx: Context,
):
    """Show debug information."""
    appglobals = cast(Globals, ctx.obj)

    config_rel_path = (
        str(appglobals.config.relative_to(os.getcwd())) if appglobals.config else None
    )

    rich.print(
        Panel(
            Group(
                f"File: {config_rel_path}",
                "Values:",
                JSON(json.dumps(appglobals.config_values)),
            ),
            title="Config",
            style="blue",
        ),
        Panel(appglobals.app, title="App", style="blue"),
    )


cli = Typer(callback=show_debug_info, invoke_without_command=True)

if __name__ == "__main__":  # pragma: no cover
    cli()
