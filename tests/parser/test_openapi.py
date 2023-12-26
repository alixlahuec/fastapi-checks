from pytest import mark, raises

from fastapi_checks.parser.openapi import (
    get_endpoint_operation_id,
    get_endpoint_security,
)


def test_get_operation_id():
    operation_id = "some_operation_id"

    assert get_endpoint_operation_id({"operationId": operation_id}) == operation_id


@mark.parametrize(
    "endpoint_spec, expected_result",
    [
        ({}, []),
        ({"security": []}, []),
        ({"security": [{"HTTPBearer": []}]}, []),
        ({"security": [{"HTTPBearer": ["some_scope"]}]}, ["some_scope"]),
    ],
)
def test_get_security(endpoint_spec, expected_result):
    from fastapi_checks.models.openapi import SecurityScheme

    assert (
        get_endpoint_security(endpoint_spec)
        == get_endpoint_security(endpoint_spec, SecurityScheme.HTTP_BEARER)
        == expected_result
    )


def test_get_security_raises_with_unsupported_scheme():
    with raises(Exception):
        get_endpoint_security({}, "some-unsupported-scheme")
