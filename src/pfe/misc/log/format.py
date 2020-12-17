import re
from traceback import format_tb
from types import TracebackType
from typing import Optional, Type, Callable

import pygments
import pygments.lexers
import pygments.formatters

from pfe.misc.log import Level, Record
from pfe.misc.style import bold, green, blue, yellow, red, gray


class Format:
    """Defines the format of records."""

    def __init__(self):
        self._levels = {
            Level.DEBUG: bold | green  | 'DEBUG',
            Level.INFO:  bold | blue   | 'INFO ',
            Level.WARN:  bold | yellow | 'WARN ',
            Level.ERROR: bold | red    | 'ERROR',
        }

        self._scope = {
            'enter': gray | '╭',
            'mid':   gray | '│',
            'exit':  gray | '╰',
        }

        self._indent = 4

    def __call__(self, record: Record, nesting: int, scope: Optional[str] = None) -> str:
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
        separator   = '  '
        level       = self._levels.get(record.level, record.level.name.upper())
        prefix      = f'{timestamp}{separator}{level}{separator}'
        placeholder = ' ' * len(clear(prefix))
        indent      = (str(self._scope['mid']) + ' ' * (self._indent - 1)) * nesting
        scope       = str(self._scope.get(scope, ' ')) + ' '

        item = str(record.item).replace('\n', f'\n{placeholder}{indent}  ')

        return f'{prefix}{indent}{scope}{item}'

    def enter(self, record: Record, nesting: int):
        return self(record, nesting, scope='enter')

    def exit(self, exception: Optional[BaseException]) -> Callable:
        def exit(record: Record, nesting: int):
            if exception is None:
                new = Record(str(bold | 'Done '), record.level)
                new = new.map(lambda x: x + f'in {(new.timestamp - record.timestamp).total_seconds()}s.')
            else:
                new = Record(f'{red | bold | type(exception).__name__}'
                             f'{red | ": " + str(exception)}', Level.ERROR)

            return self(new, nesting, scope='exit')

        return exit

    @classmethod
    def exception(cls,
                  type: Type[BaseException],
                  exception: BaseException,
                  traceback: TracebackType):
        """Formats an exception."""

        def highlight(code):
            lexer = pygments.lexers.PythonLexer()
            formatter = pygments.formatters.TerminalFormatter()

            return pygments.highlight(code, lexer, formatter)

        def form(line):
            header, code = line.split('\n', 1)

            return header + '\n' + highlight(code)

        traceback = format_tb(traceback)
        traceback = map(form, traceback)
        traceback = ''.join(traceback)

        type = highlight(type.__name__)
        type = type.rstrip('\n')

        exception = repr(exception.args)
        exception = exception.strip('(,)')
        exception = highlight(exception)

        return f'{red | "Traceback (most recent call last):"} \n\n' \
               f'{traceback} \n' \
               f'{bold | type}: {exception}'
