## Description

A small library that provides tooling to inspect and run tests against [FastAPI](https://github.com/tiangolo/fastapi) applications.

[![codecov](https://codecov.io/github/alixlahuec/fastapi-checks/graph/badge.svg?token=CvAhnsWNf9)](https://codecov.io/github/alixlahuec/fastapi-checks)

## Usage

### CLI

#### General options

| Parameter | Description |
| --------- | ----------- |
| `--app` | (Required) The location of the FastAPI instance to use. Must be provided before any commands. |
| `--config` | (Optional) The location of the config file to use. Must be provided before any commands |

```bash
fastapi-checks --app "app_example.main:app" routes
fastapi-checks --config "myconfigfile.json" debug
```

#### Using a config file

The library uses [`pycosmiconfig`](https://github.com/JuroOravec/pycosmiconfig/) to automatically detect and load configuration files.
Among other formats, it supports the following:
- a `[tool.fastapi_checks]` property in pyproject.toml
- a `fastapi_checks.json`, `fastapi_checks.yaml`, `fastapi_checks.toml` file inside a `.config` subdirectory
- a `fastapi_checks.config.py` file

See the project's homepage for the full list of supported formats.

#### Available commands

**`routes`**

View a summary of API routes. Available options:
- `--html`: render the results as an interactive table in the browser (uses [Dash](https://dash.plotly.com/)).
- `--match`: only show routes whose path matches a specific pattern.
   + This will be parsed as a regular expression (e.g., `--match "0.1"` will return all routes whose path includes `"0.1"`; `--match "^/0.1"` will return all routes whose path starts with `"/0.1"`).

```bash
fastapi-checks routes
fastapi-checks routes --html
fastapi-checks routes --match "0.1"
```

**`debug`**

Show debug information (e.g. config file, FastAPI application details).

```bash
fastapi-checks debug
```

### Test runners

The library can also be used to write tests asserting against a FastAPI application.

An example (using Pytest):

```python
from fastapi_checks.testing import FastApiChecks
from pytest import mark

from app_example.main import app  # the FastAPI app to assert against


# This is an alias for the App parser
FAC = FastApiChecks(app=app)


# Are all routes under /0.1 marked as deprecated?
@mark.parametrize(
    "api_route",
    FAC.api_routes(path_regex="^/0.1"),
)
def test_01_routes_are_deprecated(api_route):
    assert api_route.route.deprecated is True


# Are all generated operation IDs unique?
def test_unique_operation_ids():
    ids = [r.operation_id for r in FAC.api_routes()]
    ids_set = set(ids)

    assert len(ids_set) == len(ids)
```

For Pytest users, the library also exposes a `fastapi_checks` fixture. It requires declaring a fixture called `fastapi_app`, which should return a FastAPI instance.
The `fastapi_checks` fixture will return the equivalent of `FastApiChecks(app=fastapi_app)` from the example above.

```python
from pytest import fixture


@fixture
def fastapi_app():
    from app_example.main import app  # the FastAPI app to assert against
    return app


def test_01_routes_are_deprecated(fastapi_checks):
    routes = fastapi_checks.api_routes(path_regex="0.1")

    for r in routes:
        assert len(r.security) > 0
```

## Concepts

The library's core functionalities are exposed through a few Pydantic models, which can be used to interact with FastAPI concepts (e.g. dependencies, routes). Each model exposes some useful methods, as well as the original object where applicable.

### `App`

Wraps `fastapi.FastAPI`. The original FastAPI instance is available under the `app` property.

```python
from fastapi_checks.models import App
from app_example.main import app


app_instance = App(app=app)

# Get the original FastAPI object
# A lot of data is directly available, through methods like .openapi()
# See the FastAPI documentation for more information
app_instance.app

# Get all API routes
# They are returned as ApiRoute instances
app_instance.api_routes()

# Get all API routes that match a RegExp
app_instance.api_routes(path_regex="^/0.1")

# Get all dependencies (recursively), by route path
# They are returned as Dependency instances
app_instance.dependencies()

# Get all dependencies (recursively), for API routes that match a RegExp
app_instance.dependencies(path_regex="^/0.1")
```

### `ApiRoute`

Wraps `fastapi.routing.APIRoute`. The original APIRoute instance is available under the `route` property.

```python
from fastapi_checks.models import App
from app_example.main import app


app_instance = App(app=app)

api_route = app_instance.api_routes()[0]

# Get the original APIRoute object
api_route.route

# Get the generated OpenAPI spec for the route
api_route.openapi

# Get the route's operation ID
api_route.operation_id

# Get all dependencies (recursively)
api_route.dependencies

# Get all unique dependencies (recursively)
# This filters out dependencies on the same callable
api_route.unique_dependencies

# Get the names of all (unique) dependencies (recursively)
# Each value will be either a method name or a class name
api_route.dependency_names

# Get all Mark instances attached to the route's (unique) dependencies
api_route.dependency_marks

# Get the security requirements for the route
# At the moment, only the HTTPBearer scheme is supported
api_route.security()
api_route.security(scheme="HTTPBearer")

# Check if the route's patch matches a RegExp
# This is used internally in App.api_routes() or App.dependencies()
api_route.predicate(path_regex="^/0.1")
```

### `Dependency`

Wraps `fastapi.Depends`. The original callable is available under the `callable` property.

```python
from fastapi_checks.models import App
from app_example.main import app


app_instance = App(app=app)

api_route = app_instance.api_routes()[0]
dependency = api_route.dependencies()[0]

# Get the callable
dependency.callable

# Get the name of the callable
# This is used internally in ApiRoute.dependency_names()
dependency.humanized

# Get the name of the argument where the dependency is injected, if applicable
# For app-, router-, and route-level dependencies, this will be null
dependency.argname

# Get the route associated with the dependency
# assert dependency.route == api_route
dependency.route

# Get the context in which the dependency is called (directly or through nested dependencies)
# This will be either:
# - "path", for app-, router-, and route-level dependencies
# - "handler", for route handler dependencies
dependency.origin

# Get the Mark instance attached to the dependency, if it exists
# This is used internally in ApiRoute.dependency_marks()
dependency.mark

# Check if the dependency has / doesn't have certain tags
# NB: the tags must have been provided using the `mark` decorator
dependency.tags_include_all(tags=["tag1", "tag2"])
dependency.tags_exclude_all(tags=["tag3", "tag4"])
dependency.tags_include(tags=["tag1", "tag3"])
```

### `Mark`

This model facilitates working with dependencies; it doesn't map to a FastAPI concept. It enables adding markup to callables being used as FastAPI dependencies, to help answer questions like "How many endpoints rely on a dependency with [tag]?". `Mark` annotations should be created using the `mark` decorator, and are available on `Dependency` objects.

**Decorator usage:**

```python
# app_example/services/auth.py
from fastapi_checks.decorators import mark


@mark("auth")
def some_auth_dependency():
    pass


@mark("auth")
class AnotherAuthDependency:
    def __init__(*args, **kwargs):
        ...
    def __call__(*args, **kwargs):
        ...
```

**Assertions on Mark instances:**

```python
# tests/app.py
from fastapi_checks.testing import FastApiChecks
from app_example.main import app


FAC = FastApiChecks(app=app)


def test_all_routes_use_auth():
    api_routes = FAC.api_routes()
    for r in api_routes:
        assert r.dependency_marks.includes("auth"), f"{r.route.path} uses an auth dependency"
```

**Model properties:**

```python
from fastapi_checks.models import App
from app_example.main import app


app_instance = App(app=app)

api_route = app_instance.api_routes()[0]
dependency = api_route.dependencies()[0]
mark = dependency.mark

# Get the "marked" callable
mark.marked

# Get the tags attached to the callable
mark.tags
```

## Development

- Clone the repository
- Install dependencies with `poetry install`
- The following commands are available:
   + `make fixes`: lint files with Ruff
   + `make checks`: check files with Ruff
   + `make typecheck`: typecheck files with mypy
   + `make test`: run tests with Pytest
   + `make test:cov`: run tests with Pytest & report on coverage

For rapid development, you can run CLI commands against the sample FastAPI application located in `app_example`. In the root directory:

```bash
poetry run fastapi-checks routes
```

## License

This project is licensed under the terms of the MIT license.
