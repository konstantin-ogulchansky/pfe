import re
import sys
from time import sleep
from traceback import format_tb
from types import TracebackType
from typing import Optional, Type, IO, Iterable, Callable

import colorama
import pygments
import pygments.lexers
import pygments.formatters

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
        yyyy-mm-dd HH-MM-SS.ffffff INFO      A.
        yyyy-mm-dd HH-MM-SS.ffffff INFO    ╭ Nesting...
        yyyy-mm-dd HH-MM-SS.ffffff DEBUG   │     B.
        yyyy-mm-dd HH-MM-SS.ffffff ERROR   │     C.
        yyyy-mm-dd HH-MM-SS.ffffff INFO    ╰ Nesting... Done.

    :param out: a callable that will be used to write logs
                (defaults to `print`).
    :param format: an (optional) instance of ``Format`` that
                   will be used to format logs.
    :param hook: whether to hook exception handling
                 and redirect it to the logger.
    """

    def __init__(self,
                 out: IO = sys.stdout,
                 format: Optional['Format'] = None,
                 hook: bool = True):
        # For cross-platforming.
        colorama.init()

        self._out = out
        self._format = format or Format()
        self._levels = list(core.Level)
        self._nesting = 0
        self._newline = False
        self._filters = []

        # Updated the default exception hook with `on_exception`.
        if hook:
            sys.excepthook = self.on_exception

    @property
    def format(self) -> 'Format':
        """Returns the style that is used to format logs."""
        return self._format

    def level(self, *, min: Optional[core.Level] = None, enabled: Optional[Iterable[core.Level]] = None):
        """..."""
        # TODO: Add scoped level?

        levels = list(core.Level)

        if min is not None:
            levels = [x for x in levels if x.value >= min.value]
        if enabled is not None:
            levels = [x for x in levels if x in enabled]

        self._levels = levels

    def filter(self, predicate: Callable[[core.Record], bool]):
        """..."""
        self._filters.append(predicate)

    def __call__(self, record: core.Record) -> 'Scope':
        """Logs the provided `text` with the specified `tag`,
        a timestamp and an indent."""

        # Ignore records with disabled levels
        # and everything within their scopes.
        if record.level not in self._levels:
            return nothing.Scope()

        # Ignore records that do not match some filter.
        if any(not f(record) for f in self._filters):
            return nothing.Scope()

        self._out.write('\n' * self._newline)
        self._out.write(self.format(record, self._nesting))

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

        def highlight(code):
            lexer = pygments.lexers.PythonLexer()
            formatter = pygments.formatters.TerminalFormatter()

            return pygments.highlight(code, lexer, formatter)

        def form(line):
            header, code = line.split('\n', 1)

            return header + '\n' + highlight(code)

        traceback = format_tb(traceback)
        traceback = map(form, traceback)
        traceback = '\n'.join(traceback)
        traceback = str(red | traceback)

        exception = repr(exception.args)
        exception = exception.strip('(,)')

        # Print the title.
        self._out.write('\n\n')
        self._out.write(str(red('Traceback:')))

        # Print the traceback.
        self._out.write('\n\n')
        self._out.write(traceback)

        # Print the exception.
        self._out.write('\n')
        self._out.write(str(bold | highlight(type.__name__).rstrip('\n')))
        self._out.write(': ' + highlight(exception))
        self._out.write('\n')


class Format:
    """Defines the format of records."""

    def __init__(self):
        self._levels = {
            core.Level.DEBUG: bold | green  | 'DEBUG',
            core.Level.INFO:  bold | blue   | 'INFO ',
            core.Level.WARN:  bold | yellow | 'WARN ',
            core.Level.ERROR: bold | red    | 'ERROR',
        }

        self._scope = {
            'enter': gray | '╭',
            'mid':   gray | '│',
            'exit':  gray | '╰',
        }

        self._indent = 4

    def __call__(self, record: core.Record, nesting: int, scope: Optional[str] = None) -> str:
        """Formats the record as a string to log.

        :param record: the record to format.
        :param nesting: the nesting level of the record.
        :param scope: the scope of the record (e.g., 'enter' or 'exit').

        :return: the formatted record.
        """

        def clear(string: str) -> str:
            """Removes ANSI codes from the string."""
            return re.sub(r'\033\[\d+m', '', string)

        timestamp   = f'{record.timestamp}'
        separator   = ' '
        level       = self._levels.get(record.level, record.level.name.upper())
        prefix      = f'{timestamp}{separator}{level}{separator}  '
        placeholder = ' ' * len(clear(prefix))
        indent      = (str(self._scope['mid']) + ' ' * (self._indent - 1)) * nesting
        scope       = str(self._scope.get(scope, ' ')) + ' '

        item = str(record.item).replace('\n', f'\n{placeholder}{indent}  ')

        return f'{prefix}{indent}{scope}{item}'


class Scope(core.Scope):
    """Defines the scope of logs."""

    def __init__(self, log: Pretty, record: core.Record):
        super(core.Scope, self).__init__()

        self._log = log
        self._record = record

    def __enter__(self):
        """Increases the nesting level of the log."""

        format = self._log.format
        record = self._record
        nesting = self._log._nesting  # NOQA.

        old_record = format(record, nesting)
        new_record = format(record, nesting, scope='enter')

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
        format = self._log.format

        if exception is None:
            record = core.Record(str(bold | 'Done '), self._record.level)
            record = record.map(lambda x: x + f'in {(record.timestamp - self._record.timestamp).total_seconds()}s.')
        else:
            record = core.Record(f'{red | bold | type.__name__}'
                                 f'{red | ": " + str(exception)}', core.Level.ERROR)

        record = format(record, nesting, scope='exit')

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
            sleep(0.1)

        with log.info('Third nesting...'):
            sleep(0.2)

    try:
        with log.info('Fourth nesting...'):
            log.info('F.\nG.')
            raise ValueError('Whatever.')
    except ValueError:
        log.info("It's okay.")

    raise ValueError('Again?', 451)

    log.info('Finished.')  # NOQA.
