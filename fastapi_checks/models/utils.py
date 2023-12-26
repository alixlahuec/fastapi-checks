import re
from typing import Pattern


SearchRegex = Pattern | str


def regex_match(regex: SearchRegex, target: str) -> bool:
    pattern = re.compile(regex) if isinstance(regex, str) else regex
    return bool(pattern.search(target))
