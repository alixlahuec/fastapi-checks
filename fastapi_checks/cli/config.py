from importlib import import_module
from pathlib import Path
from typing import Annotated, Optional

from fastapi import FastAPI
from pycosmiconfig import cosmiconfig
from typer import Context, Option

from fastapi_checks import models


explorer = cosmiconfig("fastapi_checks", package_prop="fastapi_checks")


def parse_entrypoint(loc: str) -> models.App:
    entrypoint = loc.split(":", maxsplit=1)

    try:
        assert len(entrypoint) == 2

        mod = import_module(entrypoint[0])
        app = getattr(mod, entrypoint[1])

        assert isinstance(app, FastAPI)

    except AssertionError:
        raise Exception("Location provided is not a FastAPI instance")

    return models.App(app=app)


# (Required) The FastAPI application to run checks against.
# The app's entrypoint can be specified in config or as a CLI argument.
App = Annotated[
    models.App,
    Option(
        parser=parse_entrypoint,
        help="Location of the FastAPI app.",
        show_default=False,
        hide_input=True,
    ),
]


def load_config(path: Optional[Path], ctx: Context) -> Optional[Path]:
    # If no config file is explicitly passed, look for one
    if path is None:
        try:
            autodetect_result = explorer.search()

            assert autodetect_result is not None
            path = autodetect_result.filepath

        except AssertionError:
            print("No config file provided, could not autodetect")
            return None

    assert isinstance(path, (Path, str))

    load_result = explorer.load(path)
    if load_result.is_empty:
        raise Exception(f"Config from {path} is empty")

    resolved_config = load_result.config
    assert isinstance(resolved_config, dict)

    # This default_map is not accessible through Context when running subcommands,
    # even though the defaults are interpreted correctly.
    # To make the values available to commands e.g. debug,
    # the dict is temporarily stored in the custom obj so that it can be passed to Globals()
    ctx.default_map = resolved_config
    ctx.obj = dict(config_values=resolved_config)

    return path


# (Optional) The path to a config file.
# If not provided, pycosmiconfig rules will be used to search for one.
# This must be parsed eagerly, to allow setting required arguments (like App) via config.
ConfigFile = Annotated[
    Optional[Path],
    Option(
        is_eager=True,
        show_default=False,
        callback=load_config,
        help="Path to a config file. If none is provided, auto-detection will be used.",
        dir_okay=False,
        file_okay=True,
        exists=True,
        readable=True,
    ),
]


# Callback for the app.
# The method's docstring is used as description for the app.
# The method's args are used to run setup operations.
def setup(
    ctx: Context,
    app: App,
    config: ConfigFile = None,
) -> None:
    """Run checks against a FastAPI application."""
    loaded_config = {}
    if hasattr(ctx, "obj"):
        loaded_config = (ctx.obj or {}).get("config_values", {})

    ctx.obj = models.Globals(app=app, config=config, config_values=loaded_config)
