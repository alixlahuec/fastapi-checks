test:
	poetry run pytest .
test\:ci:
	poetry run coverage run -m pytest && poetry run coverage lcov
test\:cov:
	poetry run coverage run -m pytest -vv && poetry run coverage report --skip-covered
fixes:
	poetry run ruff format .
	poetry run ruff check . --fix-only
checks:
	poetry run ruff check .
typecheck:
	poetry run mypy .