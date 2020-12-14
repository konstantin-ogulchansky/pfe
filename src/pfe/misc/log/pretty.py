import re
import sys
from traceback import format_tb
from types import TracebackType
from typing import Optional, Type, IO, Iterable

import colorama

from pfe.misc.log import core, nothing
from pfe.misc.style import bold, green, blue, yellow, red, gray


class Pretty(core.Log):
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
    :param style: an (optional) instance of ``Style`` that
                  will be used to format logs.
    :param hook: whether to hook exception handling
                 and redirect it to the logger.
    """

    def __init__(self,
                 out: IO = sys.stdout,
                 style: Optional['Style'] = None,
                 hook: bool = True):
        # For cross-platforming.
        colorama.init()

        self._out = out
        self._style = style or Style()
        self._levels = list(core.Level)
        self._nesting = 0
        self._newline = False

        # Updated the default exception hook with `on_exception`.
        if hook:
            sys.excepthook = self.on_exception

    @property
    def style(self) -> 'Style':
        """Returns the style that is used to format logs."""
        return self._style

    def level(self, *, min: Optional[core.Level] = None, enabled: Optional[Iterable[core.Level]] = None):
        """..."""
        # TODO: Add scoped level?

        levels = list(core.Level)

        if min is not None:
            levels = [x for x in levels if x.value >= min.value]
        if enabled is not None:
            levels = [x for x in levels if x in enabled]

        self._levels = levels

    def __call__(self, record: core.Record) -> 'Scope':
        """Logs the provided `text` with the specified `tag`,
        a timestamp and an indent."""

        # Ignore records with disabled levels
        # and everything within their scopes.
        if record.level not in self._levels:
            return nothing.Scope()

        self._out.write('\n' * self._newline)
        self._out.write(self.style.format(record, self._nesting))

        self._newline = True

        return Scope(self, record)

    def increase_nesting(self):
        """Increases the nesting level and returns it."""

        self._nesting += 1
        return self._nesting

    def decrease_nesting(self):
        """Decreases the nesting level and returns it."""

        self._nesting -= 1
        return self._nesting

    def on_exception(self,
                     type: Type[BaseException],
                     exception: BaseException,
                     traceback: TracebackType):
        """A hook that is called on an exception."""

        traceback = format_tb(traceback)
        traceback = '\n'.join(traceback)
        traceback = str(red | traceback)

        # Print the title.
        self._out.write('\n\n')
        self._out.write(str(red('Traceback:')))

        # Print the traceback.
        self._out.write('\n\n')
        self._out.write(traceback)

        # Print the exception.
        self._out.write('\n')
        self._out.write(str(bold | red | type.__name__))
        self._out.write(str(red(': ' + str(exception))))
        self._out.write('\n')


class Style:
    """Defines the style of records."""

    def __init__(self):
        self._levels = {
            core.Level.DEBUG: bold | green  | 'DEBUG',
            core.Level.INFO:  bold | blue   | 'INFO ',
            core.Level.WARN:  bold | yellow | 'WARN ',
            core.Level.ERROR: bold | red    | 'ERROR',
        }

        self._scope = {
            'enter': str(gray('╭')),
            'mid':   str(gray('│')),
            'exit':  str(gray('╰')),
        }

        self._indent = 4

    def format(self, record: core.Record, nesting: int, scope: Optional[str] = None) -> str:
        """Formats the record as a string to log.

        :param record: the record to format.
        :param nesting: the nesting level of the record.
        :param scope: the scope of the record (e.g., 'enter' or 'exit').

        :return: the formatted record.
        """

        def clear(string: str) -> str:
            """Removes ANSI codes from the string."""
            return re.sub(r'\033\[\d+m', '', string)

        timestamp   = f'[{record.timestamp}]'
        level       = self._levels.get(record.level, record.level.name.upper())
        placeholder = ' ' * len(clear(f'{timestamp} {level}'))
        indent      = (self._scope['mid'] + ' ' * (self._indent - 1)) * nesting
        scope       = self._scope.get(scope, ' ')

        item = str(record.item).replace('\n', f'\n{placeholder} {indent}  ')

        return f'{timestamp} {level} {indent}{scope} {item}'


class Scope(core.Scope):
    """Defines the scope of logs."""

    def __init__(self, log: Pretty, record: core.Record):
        super(core.Scope, self).__init__()

        self._log = log
        self._record = record

    def __enter__(self):
        """Increases the nesting level of the log."""

        style = self._log.style
        record = self._record
        nesting = self._log._nesting  # NOQA.

        old_record = style.format(record, nesting)
        new_record = style.format(record, nesting, scope='enter')

        # Remove the old record and replace it with the new one.
        self._log._out.write('\b' * len(old_record))  # NOQA.
        self._log._out.write(new_record)              # NOQA.

        self._log.increase_nesting()

    def __exit__(self,
                 type: Type[BaseException],
                 exception: BaseException,
                 traceback: TracebackType):
        """Decreases the nesting level and prints the log."""

        nesting = self._log.decrease_nesting()
        style = self._log.style

        if exception is None:
            record = self._record.refreshed()
            record = record.map(lambda x: x + str(bold | ' Done.'))
        else:
            record = core.Record(self._record.item, core.Level.ERROR)
            record = record.map(lambda x: x + f' {red | bold | type.__name__}'
                                              f'{red | ": " + str(exception)}')

        record = style.format(record, nesting, scope='exit')

        self._log._out.write('\n')    # NOQA.
        self._log._out.write(record)  # NOQA.


if __name__ == '__main__':
    log = Pretty()
    log.debug('Starting...\nYeah.')

    with log.info('First nesting...'):
        log.info('A.')
        log.info('B.')

        with log.warn('Second nesting...'):
            log.error('C.\nD.\nE.')

        with log.info('Third nesting...'):
            pass

    try:
        with log.info('Fourth nesting...'):
            log.info('F.\nG.')
            raise ValueError('Whatever.')
            log.info('H.')  # NOQA.
    except ValueError:
        log.info("It's okay.")

    log.info('Finished.')
