from typing import Callable, Iterable

from pydantic import BaseModel, Extra


class Mark(BaseModel, extra=Extra.allow):
    marked: Callable
    _tags: set[str] = set()

    @property
    def tags(self) -> list[str]:
        return sorted(self._tags)

    def add_tags(self, tags: Iterable[str]) -> None:
        self._tags = self._tags.union(set(tags))

    def predicate(
        self,
        *,
        tags_include: Iterable[str] = {},
        tags_include_all: Iterable[str] = {},
        tags_exclude_all: Iterable[str] = {},
    ) -> bool:
        if tags_include_all:
            return set(tags_include_all).issubset(self._tags)
        elif tags_exclude_all:
            return set(tags_exclude_all).isdisjoint(self._tags)
        elif tags_include:
            return bool(set(tags_include).intersection(self._tags))
        else:
            return True
