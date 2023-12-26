from pytest import raises


def test_missing_fastapi_app_fixture_raises(request):
    with raises(Exception) as exc:
        request.getfixturevalue("fastapi_app")

    assert "fastapi_app fixture is not defined" in exc.exconly()
