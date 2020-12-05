"""
Contains functions for logging.
"""

from contextlib import contextmanager
from datetime import datetime
from typing import Any, Callable, ContextManager


def nothing(*args: Any, **kwargs: Any):
    """Writes nothing (a convenient function to reduce
    the number of `if` statements)."""


def timestamped(*args: Any, **kwargs: Any):
    """Writes a timestamped log to the standard output (via `print`)."""
    print(f'[{datetime.now()}]', *args, **kwargs)


@contextmanager
def cx(log: Callable, *args: Any, **kwargs: Any) -> ContextManager:
    """Used to log the start and the end of an operation."""

    log(*args, **kwargs)

    try:
        yield
    finally:
        log(*args, 'Done.', **kwargs)
