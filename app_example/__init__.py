from pydantic import BaseConfig


class Config(BaseConfig):
    api_origin: str = "http://example.com"
