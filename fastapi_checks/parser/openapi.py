from fastapi_checks.models.openapi import Endpoint, SecurityScheme


def get_endpoint_operation_id(openapi_endpoint: Endpoint) -> str:
    return openapi_endpoint.get("operationId") or ""


def get_endpoint_security(
    openapi_endpoint: Endpoint, scheme: SecurityScheme = SecurityScheme.HTTP_BEARER
) -> list[str]:
    security_requirements = (
        openapi_endpoint["security"] if "security" in openapi_endpoint else []
    )

    if scheme == SecurityScheme.HTTP_BEARER:
        return [
            scope
            for spec in security_requirements
            for scope in spec["HTTPBearer"]
            if spec["HTTPBearer"]
        ]
    else:
        raise (
            f"Security scheme {scheme} is not supported. Please use one of {SecurityScheme.__members__}"
        )
