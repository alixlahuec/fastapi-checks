from typing import Any, Literal

import rich
from rich.table import Table as RichTable
from dash.dash_table import DataTable as DashTable
from pydantic import BaseModel


class Column(BaseModel):
    label: str
    align_header: str = "center"
    align_data: str = "left"
    width: str = "auto"

    # html only
    sort: Literal["asc"] | Literal["desc"] | None = None
    style_data: dict[str, Any] = {}

    # rich only
    rich_theme: str | None = None

    @property
    def id(self) -> str:
        return self.label.lower().replace(" ", "_")

    class DataTableConfig(BaseModel):
        id: str
        name: str
        type: str = "text"
        presentation: str = "input"

    def html_config(self) -> dict:
        conf = self.DataTableConfig(id=self.id, name=self.label)
        return conf.dict()

    def html_sort_by(self) -> dict[str, str] | None:
        if self.sort:
            return {"column_id": self.id, "direction": self.sort}

        return None

    def html_style_data(self) -> dict[str, Any]:
        return {
            "if": {"column_id": self.id},
            "width": self.width,
            "textAlign": self.align_data,
            **self.style_data,
        }

    def html_style_header(self) -> dict[str, Any]:
        return {
            "if": {"column_id": self.id},
            "textAlign": self.align_header,
        }


class Table(BaseModel):
    columns: list[Column]
    cells: list[dict] = []

    html_css: list[dict] = []

    @property
    def column_ids(self) -> list[str]:
        return [col.id for col in self.columns]

    def add_row(self, *values: tuple) -> None:
        row = {k: v for k, v in zip(self.column_ids, values, strict=True)}
        self.cells.append(row)

    def html(self) -> DashTable:
        return DashTable(
            columns=[col.html_config() for col in self.columns],
            data=self.cells,
            css=self.html_css,
            style_as_list_view=True,
            style_cell={
                "fontWeight": "500",
            },
            style_data={
                "padding": "10px",
                # wrap cells contents
                "whiteSpace": "normal",
                "height": "auto",
            },
            style_data_conditional=[col.html_style_data() for col in self.columns],
            style_header={
                "fontWeight": "bold",
                "padding": "10px",
            },
            style_header_conditional=[col.html_style_header() for col in self.columns],
            style_filter={
                "padding": "8px 15px",
                "opacity": "0.7",
            },
            sort_action="none",
            sort_by=[col.html_sort_by() for col in self.columns if col.html_sort_by()],
            filter_action="native",
            filter_options={"placeholder_text": "Search..."},
            page_action="native",
        )

    def rich(self) -> RichTable:
        rtable = RichTable(box=rich.box.MINIMAL, expand=True)

        for col in self.columns:
            rtable.add_column(col.label, style=col.rich_theme)

        for row in self.cells:
            rtable.add_row(*list(row.values()))

        return rtable
