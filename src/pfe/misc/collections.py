"""
Contains auxiliary functions for processing collections.
"""

from typing import Callable


def unique(x: list, select: Callable) -> list:
    """..."""

    seen = set()
    result = []

    for item in x:
        if (id := select(item)) not in seen:
            seen.add(id)
            result.append(item)

    return result
