from contextlib import contextmanager

import dash_bootstrap_components as dbc
from dash import Dash


@contextmanager
def run_dash(title: str):
    app = Dash(
        __name__,
        title=title,
        external_stylesheets=[
            dbc.themes.SUPERHERO,
            "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css",
        ],
    )

    def render(children) -> None:
        app.layout = dbc.Container(
            children,
            className="dbc p-5",
        )

    yield render

    app.run(debug=True)
