import sys
from contextlib import nullcontext
from time import sleep
from types import TracebackType
from typing import Optional, Type, IO, Iterable, Callable, Union, Any, ContextManager

import colorama

from pfe.misc.log import Log, Record, Level, Format


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
        yyyy-mm-dd HH-MM-SS.ffffff  INFO      A.
        yyyy-mm-dd HH-MM-SS.ffffff  INFO    ╭ Nesting...
        yyyy-mm-dd HH-MM-SS.ffffff  DEBUG   │     B.
        yyyy-mm-dd HH-MM-SS.ffffff  ERROR   │     C.
        yyyy-mm-dd HH-MM-SS.ffffff  INFO    ╰ Nesting... Done.

    :param out: an IO stream to write logs to
                (defaults to ``stdout``).
    :param format: an (optional) instance of ``Format`` that
                   will be used to format logs.
    :param hook: whether to hook exception handling
                 and redirect it to the logger.
    """

    class Scope(Log.Scope):

        class Cx:

            def __init__(self, log: 'Pretty', item: Any):
                self._log = log
                self._item = item

            def __enter__(self):
                self._log(self._item, format=self._log.format.enter)
                self._log._nesting += 1

            def __exit__(self, type: Type[BaseException], exception: BaseException, traceback: TracebackType):
                self._log._nesting -= 1
                self._log(self._item, format=self._log.format.exit(exception))

        def __init__(self, log: 'Pretty'):
            self._log = log

        def __call__(self, item: Union[Any, Record]) -> ContextManager:
            if isinstance(item, Record) and self._log.ignored(item):
                return nullcontext()
            else:
                return Pretty.Scope.Cx(self._log, item)

    def __init__(self,
                 out: IO = sys.stdout,
                 format: Optional['Format'] = None,
                 hook: bool = True):
        self._out = out
        self._format = format or Format()
        self._levels = list(Level)
        self._nesting = 0
        self._filters = []

        # For cross-platform ANSI support.
        colorama.init()

        # Updated the default exception hook.
        if hook:
            def excepthook(*args, **kwargs):
                self._out.write('\n')
                self._out.write(self._format.exception(*args, **kwargs))

            sys.excepthook = excepthook

    @property
    def format(self) -> 'Format':
        """Returns the style that is used to format logs."""
        return self._format

    @property
    def scope(self) -> 'Log.Scope':
        """TODO."""
        return Pretty.Scope(self)

    def level(self, *, min: Optional[Level] = None, enabled: Optional[Iterable[Level]] = None):
        """TODO."""

        levels = list(Level)

        if min is not None:
            levels = [x for x in levels if x.value >= min.value]
        if enabled is not None:
            levels = [x for x in levels if x in enabled]

        self._levels = levels

    def filter(self, predicate: Callable[[Record], bool]):
        """TODO."""
        self._filters.append(predicate)

    def ignored(self, item: Union[Any, Record]) -> bool:
        """TODO."""

        if isinstance(item, Record):
            # Ignore records with disabled levels
            # and everything within their scopes.
            if item.level not in self._levels:
                return True

            # Ignore records that do not match some filter.
            if any(not f(item) for f in self._filters):
                return True

        return False

    def __call__(self, item: Union[Any, Record], format: Optional[Callable] = None):
        """Logs the provided ``item`` with the specified,
        a timestamp and an indent."""

        if isinstance(item, Record):
            # Do not log ignored records.
            if self.ignored(item):
                return

            text = (format or self._format)(item, self._nesting)
        else:
            text = str(item)

        self._out.write(text + '\n')


if __name__ == '__main__':
    log = Pretty()
    log.debug('Starting...\nYeah.')

    with log.scope.info('First nesting...'):
        log.info('A.')
        log.info('B.')

        with log.scope.warn('Second nesting...'):
            log.error('C.\nD.\nE.')
            sleep(0.1)

        with log.scope.info('Third nesting...'):
            sleep(0.2)

    try:
        with log.scope.info('Fourth nesting...'):
            log.info('F.\nG.')
            raise ValueError('Whatever.')
    except ValueError:
        log.info("It's okay.")

    raise ValueError('Again?', 451)

    log.info('Finished.')  # NOQA.
