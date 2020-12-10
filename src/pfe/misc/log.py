"""
Contains functions for logging.
"""

from abc import ABCMeta, abstractmethod
from contextlib import nullcontext
from datetime import datetime
from typing import ContextManager, Callable, Any

import colorama

from pfe.misc.style import red, green, blue, yellow, gray, bold, StyledText


class Log(metaclass=ABCMeta):
    """An interface of all loggers.

    Each of the methods return a context manager that can be used
    to write nested logs. See, for example, `Pretty(Log)`.
    """

    def debug(self, text: Any) -> ContextManager:
        """Logs `text` with the 'DEBUG' tag."""
        return self('DEBUG', text)

    def info(self, text: Any) -> ContextManager:
        """Logs `text` with the 'INFO' tag."""
        return self('INFO', text)

    def warn(self, text: Any) -> ContextManager:
        """Logs `text` with the 'WARN' tag."""
        return self('WARN', text)

    def error(self, text: Any) -> ContextManager:
        """Logs `text` with the 'ERROR' tag."""
        return self('ERROR', text)

    @abstractmethod
    def __call__(self, tag: Any, text: Any) -> ContextManager:
        """Logs the provided `text` with the specified `tag`."""


class Nothing(Log):
    """Logs nothing (used to avoid `None` checks)."""

    def __call__(self, tag: Any, text: Any) -> ContextManager:
        """Does literally nothing."""
        return nullcontext()


class Pretty(Log):
    """Logs pretty colored and timestamped text.

    For example, the output of the following code
    ::
        log = Pretty()
        log.debug('A.')

        with log.info('Nesting...'):
            log.warn('B.')
            log.warn('C.')

    will be
    ::
        [yyyy-mm-dd HH-MM-SS.ffffff] DEBUG   A.
        [yyyy-mm-dd HH-MM-SS.ffffff] INFO    Nesting...
        [yyyy-mm-dd HH-MM-SS.ffffff] WARN    |   B.
        [yyyy-mm-dd HH-MM-SS.ffffff] WARN    |   C.
        [yyyy-mm-dd HH-MM-SS.ffffff] INFO    Nesting... Done.

    :param indent: the size of an indent that will be used when the
                    nesting level is increased (defaults to 4).
    :param out: a callable that will be used to write logs
                (defaults to `print`).
    """

    # Justification width for tags.
    TAG_WIDTH = 7

    class Cx:
        """Manages the indent of logs."""

        def __init__(self, log: 'Pretty', tag: Any, text: Any, done: Any = 'Done.'):
            self._log = log
            self._tag = tag
            self._text = text
            self._done = lambda x: str(x) + ' ' + str(done)

        def done(self, f: Callable) -> 'Pretty.Cx':
            self._done = f
            return self

        def __enter__(self):
            """Increases the nesting level of the log."""
            self._log._nesting += 1  # NOQA.

        def __exit__(self, exc_type, exc_val, exc_tb):
            """Decreases the nesting level and prints the log."""

            self._log._nesting -= 1  # NOQA.
            self._log(self._tag, self._done(self._text))

    def __init__(self, out: Callable = print, indent: int = 4):
        if indent < 1:
            raise ValueError(f'`indent` must be at least 1, got {indent}.')

        # For cross-platforming.
        colorama.init()

        self._out = out
        self._indent = indent
        self._nesting = 0

    def debug(self, text: Any) -> ContextManager:
        return self(bold | green | 'DEBUG', text)

    def info(self, text: Any) -> ContextManager:
        return self(bold | blue | 'INFO', text)

    def warn(self, text: Any) -> ContextManager:
        return self(bold | yellow | 'WARN', text)

    def error(self, text: Any) -> ContextManager:
        return self(bold | red | 'ERROR', text)

    def __call__(self, tag: Any, text: Any) -> ContextManager:
        """Logs the provided `text` with the specified `tag`,
        a timestamp and an indent."""

        if isinstance(tag, str):
            tag = tag.ljust(self.TAG_WIDTH)
        if isinstance(tag, StyledText):
            tag = tag.map(lambda x: x.ljust(self.TAG_WIDTH))

        timestamp = f'[{datetime.now()}]'

        indent = str(gray('|')) + ' ' * (self._indent - 1)
        indent = indent * self._nesting

        self._out(timestamp, tag, indent + str(text))

        return Pretty.Cx(self, tag, text)


if __name__ == '__main__':
    log: Log = Pretty()
    log.info('Starting...')

    with log.debug('First nesting...'):
        log.info('A.')
        log.info('B.')

        with log.error('Second nesting...'):
            log.warn('C.')
            log.warn('D.')

        with log.info('Third nesting...'):
            log.error('E.')

    log.info('Finished.')
