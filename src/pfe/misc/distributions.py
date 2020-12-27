"""
Contains functions that allow defining different discrete distributions.
"""

from typing import Callable

import numpy as np


def constant(value: int) -> Callable[[], int]:
    """Returns a function that always returns the same ``value``."""

    def next() -> int:
        return value

    return next


def uniform(*values: int) -> Callable[[], int]:
    """Returns a function that uniformly picks a value
    from the provided list of ``values``."""

    def next() -> int:
        return np.random.choice(values)

    return next


def normal(loc: float, scale: float) -> Callable[[], int]:
    """Returns a function that generates integer random values according to
    the normal (Gaussian) distribution with parameters ``loc`` and ``scale``."""

    def next() -> int:
        return round(np.random.normal(loc=loc, scale=scale))

    return next
