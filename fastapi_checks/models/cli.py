from pathlib import Path
from typing import Any, Optional

from pydantic import BaseModel

from fastapi_checks.models.app import App


class Globals(BaseModel):
    app: App
    config: Optional[Path] = None
    config_values: dict[str, Any] = dict()
