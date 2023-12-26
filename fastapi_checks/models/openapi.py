from enum import Enum
from typing import Any


class SecurityScheme(str, Enum):
    HTTP_BEARER = "HTTPBearer"


Endpoint = dict[str, Any]
