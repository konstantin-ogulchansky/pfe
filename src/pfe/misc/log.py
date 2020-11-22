"""
Contains functions for logging.
"""

from typing import Any
from datetime import datetime


def nothing(*args: Any, **kwargs: Any):
    """Writes nothing (a convenient function to reduce
    the number of `if` statements)."""


def timestamped(*args: Any, **kwargs: Any):
    """Writes a timestamped log to the standard output (via `print`)."""
    print(f'[{datetime.now()}]', *args, **kwargs)
