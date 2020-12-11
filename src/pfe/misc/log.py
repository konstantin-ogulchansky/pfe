"""
Contains functions for logging.
"""

import sys
from abc import ABCMeta, abstractmethod
from contextlib import redirect_stderr
from datetime import datetime
from io import StringIO
from traceback import format_tb
from types import TracebackType
from typing import ContextManager, Any, IO, Type, Optional, Callable

import colorama

from pfe.misc.style import red, green, blue, yellow, gray, bold


class Log(metaclass=ABCMeta):
    """An interface of all loggers."""

    class Record:
        """A timestamped record to be logged by the logger.

        :param tag: a tag of a record (e.g., 'info', 'warn', 'error', etc.).
        :param item: an item to log (any object that can be converted to `str`).
        """

        def __init__(self, tag: str, item: Any, timestamp: Optional[datetime] = None):
            self._tag = tag
            self._item = item
            self._timestamp = timestamp or datetime.now()

        @property
        def tag(self) -> Any:
            """Returns the tag."""
            return self._tag

        @property
        def item(self) -> Any:
            """Returns the item."""
            return self._item

        @property
        def timestamp(self) -> datetime:
            """Returns the timestamp."""
            return self._timestamp

        def map(self, function: Callable) -> 'Log.Record':
            """..."""
            return type(self)(self._tag, function(self._item), self._timestamp)

        def refreshed(self) -> 'Log.Record':
            """Returns a new record with a refreshed timestamp."""
            return type(self)(self._tag, self._item)

    class Scope(metaclass=ABCMeta):
        """..."""

        def __init__(self):
            self._done = None
            self._error = None

        def done(self, function: Callable[[str], Any]) -> 'Log.Scope':
            """..."""

            self._done = function
            return self

        def error(self, function: Callable) -> 'Log.Scope':
            """..."""

            self._error = function
            return self

        @abstractmethod
        def __enter__(self):
            """..."""

        @abstractmethod
        def __exit__(self,
                     exc_type: Optional[Type[BaseException]],
                     exc_val: Optional[BaseException],
                     exc_tb: Optional[TracebackType]):
            """..."""

    def debug(self, item: Any) -> Scope:
        """Logs `text` with the 'DEBUG' tag."""
        return self(self.Record('debug', item))

    def info(self, item: Any) -> Scope:
        """Logs `text` with the 'INFO' tag."""
        return self(self.Record('info', item))

    def warn(self, item: Any) -> Scope:
        """Logs `text` with the 'WARN' tag."""
        return self(self.Record('warn', item))

    def error(self, item: Any) -> Scope:
        """Logs `text` with the 'ERROR' tag."""
        return self(self.Record('error', item))

    @abstractmethod
    def __call__(self, record: Record) -> Scope:
        """Logs the provided `text` with the specified `tag`."""


class Nothing(Log):
    """Logs nothing (used to avoid `None` checks)."""

    class Scope(Log.Scope):
        def __enter__(self): pass
        def __exit__(self, *_: Any): pass

    def __call__(self, record: Log.Record) -> Log.Scope:
        """Does literally nothing."""
        return Nothing.Scope()


class Pretty(Log):
    """Logs pretty colored and timestamped text.

    For example, the output of the following code
    ::
        log = Pretty()
        log.info('A.')

        with log.info('Nesting...'):
            log.debug('B.')
            log.error('C.')

    will be
    ::
        [yyyy-mm-dd HH-MM-SS.ffffff] INFO    A.
        [yyyy-mm-dd HH-MM-SS.ffffff] INFO  ╭ Nesting...
        [yyyy-mm-dd HH-MM-SS.ffffff] DEBUG │     B.
        [yyyy-mm-dd HH-MM-SS.ffffff] ERROR │     C.
        [yyyy-mm-dd HH-MM-SS.ffffff] INFO  ╰ Nesting... Done.

    :param out: a callable that will be used to write logs
                (defaults to `print`).
    :param hook: whether to hook exception handling
                 and redirect it to the logger.
    """

    class Record(Log.Record):

        TAGS = {
            'debug': bold | green  | 'DEBUG',
            'info':  bold | blue   | 'INFO ',
            'warn':  bold | yellow | 'WARN ',
            'error': bold | red    | 'ERROR',
        }

        SCOPE = {
            'enter': str(gray('╭')),  # Another option: ┌
            'mid':   str(gray('│')),  # Another option: ├
            'exit':  str(gray('╰')),  # Another option: └
            'none':  ' '
        }

        INDENT = SCOPE['mid'] + '   '

        def format(self, nesting: int, scope: str = 'none') -> str:
            """Formats the record as a string to log.

            :param nesting: the nesting level of the record.
            :param scope: the scope of the record ('enter', 'exit' or 'none').

            :return: formatted record.
            """

            indent = self.INDENT * nesting
            scope = self.SCOPE[scope]
            tag = self.TAGS.get(self._tag, self._tag.upper())

            return f'[{self._timestamp}] {tag} {indent}{scope} {self._item}'

    class Scope(Log.Scope):
        """Manages the scope of logs."""

        def __init__(self, log: 'Pretty', record: 'Pretty.Record'):
            super(Log.Scope, self).__init__()

            self._log = log
            self._record = record

            def done(record: str) -> Any:
                return record + str(bold | f' Done.')

            def error(record: str, exception: BaseException) -> Any:
                return record + str(bold | f' Erred with `{red | type(exception).__name__}`.')

            self._done = done
            self._error = error

        def __enter__(self):
            """Increases the nesting level of the log."""

            record = self._record
            nesting = self._log._nesting

            # Remove the last line.
            self._log._out.write('\b' * len(record.format(nesting)))
            self._log._out.write(record.format(nesting, scope='enter'))

            self._log.increase_nesting()

        def __exit__(self, _: Type[BaseException], exception: BaseException, traceback: TracebackType):
            """Decreases the nesting level and prints the log."""

            nesting = self._log.decrease_nesting()

            if exception is None:
                record = self._record.refreshed()
                record = record.map(self._done)

                formatted = record.format(nesting, scope='exit')

                self._log._out.write(self._log._newline)
                self._log._out.write(formatted)

            else:
                record = Pretty.Record('error', self._record.item)
                record = record.map(lambda x: self._error(x, exception))

                formatted = record.format(nesting, scope='exit')

                self._log._out.write(self._log._newline)
                self._log._out.write(formatted)

    def __init__(self, out: IO = sys.stdout, hook: bool = True):
        # For cross-platforming.
        colorama.init()

        self._out = out
        self._nesting = 0
        self._newline = ''

        # Updated the default exception hook with `on_exception`.
        if hook:
            sys.excepthook = self.on_exception

    def __call__(self, record: Record) -> Scope:
        """Logs the provided `text` with the specified `tag`,
        a timestamp and an indent."""

        self._out.write(self._newline)
        self._out.write(record.format(self._nesting))

        self._newline = '\n'

        return Pretty.Scope(self, record)

    def increase_nesting(self):
        """Increases the nesting level and returns it."""
        self._nesting += 1
        return self._nesting

    def decrease_nesting(self):
        """Decreases the nesting level and returns it."""
        self._nesting -= 1
        return self._nesting

    def on_exception(self, type: Type[BaseException], exception: BaseException, traceback: TracebackType):
        """A hook that is called on an exception."""

        traceback = format_tb(traceback)
        traceback = '\n'.join(traceback)
        traceback = str(red | traceback)

        # Print the title.
        self._out.write(self._newline * 2)
        self._out.write(str(red('Traceback:')))

        # Print the traceback.
        self._out.write(self._newline * 2)
        self._out.write(traceback)

        # Print the exception.
        self._out.write(self._newline)
        self._out.write(str(bold | red | type.__name__))
        self._out.write(str(red(': ' + str(exception))))
        self._out.write(self._newline)


def redirect_stderr_to(log: Log, map: Optional[Callable[[str], Any]] = None) -> ContextManager:
    """Redirects the `stderr` stream to the provided log.

    Only non-space strings are redirected to `log`.

    :param log: ...
    :param map: ...
    """

    class EventIO(StringIO):

        def __init__(self, sub):
            super().__init__()
            self._sub = sub

        def write(self, __s: str) -> int:
            result = super(EventIO, self).write(__s)
            self._sub(__s)
            return result

    event = EventIO(lambda x: log.warn(map(x)) if not x.isspace() else ...)

    cx = redirect_stderr(event)
    cx.__enter__()

    return cx


if __name__ == '__main__':
    log: Log = Pretty()
    log.debug('Starting...')

    with log.info('First nesting...'):
        log.info('A.')
        log.info('B.')

        with log.warn('Second nesting...'):
            log.error('C.')

        with log.info('Third nesting...'):
            pass

    with log.info('Fourth nesting...'):
        log.info('D.')
        raise ValueError('Whatever.')
        log.info('E.')  # NOQA.

    log.info('Finished.')
