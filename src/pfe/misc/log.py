"""
Contains functions for logging.
"""

from abc import ABCMeta, abstractmethod
from contextlib import nullcontext
from datetime import datetime
from types import TracebackType
from typing import ContextManager, Any, IO, Type
from sys import stdout

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
        [yyyy-mm-dd HH-MM-SS.ffffff] INFO  ╭ Nesting...
        [yyyy-mm-dd HH-MM-SS.ffffff] WARN  │     B.
        [yyyy-mm-dd HH-MM-SS.ffffff] WARN  │     C.
        [yyyy-mm-dd HH-MM-SS.ffffff] INFO  ╰ Nesting... Done.

    :param indent: the size of an indent that will be used when the
                    nesting level is increased (defaults to 4).
    :param out: a callable that will be used to write logs
                (defaults to `print`).
    """

    # Justification width for tags.
    TAG_WIDTH = 5

    # Symbols used to write nested logs.
    NESTED_ENTER = str(gray('╭'))  # Another option: ┌.
    NESTED       = str(gray('│'))
    NESTED_EXIT  = str(gray('╰'))  # Another option: └.

    class Record:
        """A record to log."""

        def __init__(self, log: 'Pretty', tag: Any, text: Any):
            self._log = log
            self._tag = tag
            self._text = text
            self._timestamp = datetime.now()

        def format(self, nesting: str = ' ') -> str:
            """Formats a string to log."""

            tag = self._tag
            text = self._text

            if isinstance(tag, str):
                tag = tag.ljust(Pretty.TAG_WIDTH)
            if isinstance(tag, StyledText):
                tag = tag.map(lambda x: x.ljust(Pretty.TAG_WIDTH))

            indent = Pretty.NESTED + ' ' * (self._log._indent - 1)
            indent = indent * self._log._nesting

            return f'[{self._timestamp}] {tag} {indent}{nesting} {text}'

        def refreshed(self) -> 'Pretty.Record':
            """Refreshes the timestamp of a record."""
            return Pretty.Record(self._log, self._tag, self._text)

    class Cx:
        """Manages the indent of logs."""

        def __init__(self, log: 'Pretty', record: 'Pretty.Record'):
            self._log = log
            self._record = record

        def __enter__(self):
            """Increases the nesting level of the log."""

            record = self._record

            # Remove the last line.
            self._log._out.write('\b' * len(record.format()))
            self._log._out.write(record.format(Pretty.NESTED_ENTER))

            self._log._nesting += 1

        def __exit__(self, exc_type: Type[BaseException], exc_val: BaseException, exc_tb: TracebackType):
            """Decreases the nesting level and prints the log."""

            record = self._record.refreshed()

            self._log._nesting -= 1

            self._log._out.write(self._log._newline)
            self._log._out.write(record.format(Pretty.NESTED_EXIT) + str(bold | ' Done.'))

    def __init__(self, out: IO = stdout, indent: int = 4):
        if indent < 1:
            raise ValueError(f'`indent` must be at least 1, got {indent}.')

        # For cross-platforming.
        colorama.init()

        self._out = out
        self._indent = indent
        self._nesting = 0
        self._newline = ''

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

        record = Pretty.Record(self, tag, text)

        self._out.write(self._newline)
        self._out.write(record.format())

        self._newline = '\n'

        return Pretty.Cx(self, record)


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
