"""
Contains auxiliary functions for processing collections.
"""

from typing import Optional, Any, Callable


def truncate(x: dict[int, Any],
             min: Optional[float] = None,
             max: Optional[float] = None) -> dict[int, Any]:
    """..."""

    if min is None and max is None:
        return dict(x)  # A copy of the original dictionary.

    def in_range(x):
        if min is not None and x < min:
            return False
        if max is not None and x > max:
            return False
        return True

    return {
        x: y for x, y in x.items()
        if in_range(x)
    }


def unique(x: list, select: Callable) -> list:
    """..."""

    seen = set()
    result = []

    for item in x:
        if (id := select(item)) not in seen:
            seen.add(id)
            result.append(item)

    return result
