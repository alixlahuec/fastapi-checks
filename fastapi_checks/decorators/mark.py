from typing import Callable, Sequence, cast

from fastapi_checks.models import Mark


MARK_METADATA_KEY = "__fastapi_checks__mark"


def mark(*args: Sequence[str]):
    """Decorator to add `fastapi_checks` metadata.

    Use this to annotate application code (e.g. dependencies).
    Multiple marks are supported.

    Example:
        ```
        import fastapi_checks

        @fastapi_checks.mark("tenant_compatible", "security)
        def some_auth_dependency():
            pass
        ```
    """

    def decorator(cbl: Callable) -> Callable:
        if not hasattr(cbl, MARK_METADATA_KEY):
            setattr(cbl, MARK_METADATA_KEY, Mark(marked=cbl))

        mark_instance = getattr(cbl, MARK_METADATA_KEY)
        cast(Mark, mark_instance)

        mark_instance.add_tags(args)

        return cbl

    return decorator
