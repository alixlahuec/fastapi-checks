from fastapi_checks import models


def test_app_no_routes(root_app):
    app = models.App(app=root_app)

    assert app.app == root_app
    assert app.api_routes() == []
    assert app.dependencies() == dict()


def test_app_simple_route(root_app, path_handler, route_path):
    root_app.get(route_path)(path_handler)
    app_instance = models.App(app=root_app)

    assert len(app_instance.api_routes()) == 1
    assert app_instance.dependencies() == {route_path: []}


def test_app_route_with_dependency(root_app, handler_with_dependency, route_path):
    root_app.get(route_path)(handler_with_dependency)
    app_instance = models.App(app=root_app)

    assert len(app_instance._all_api_routes) == 1

    deps = app_instance.dependencies()
    assert len(deps.keys()) == 1
    assert all([isinstance(x, models.Dependency) for x in deps.get(route_path)])

    assert len(app_instance.api_routes(path_regex=route_path)) == 1
    assert len(app_instance.api_routes(path_regex="otherpath")) == 0
