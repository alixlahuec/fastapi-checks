from fastapi import FastAPI
from fastapi.routing import APIRoute

from fastapi_checks.models import ApiRoute


def get_api_routes(app: FastAPI) -> list[ApiRoute]:
    openapi_spec = app.openapi()

    return [
        ApiRoute(
            route=route,
            openapi=openapi_spec["paths"][route.path][
                next(iter(route.methods)).lower()
            ],
        )
        for route in app.routes
        if isinstance(route, APIRoute)
    ]
