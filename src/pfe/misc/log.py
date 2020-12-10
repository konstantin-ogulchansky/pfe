"""
Contains functions for logging.
"""

from abc import ABCMeta, abstractmethod
from contextlib import nullcontext
from datetime import datetime
from typing import ContextManager, Callable, Union, Any

import colorama


class Log(metaclass=ABCMeta):
    """..."""

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
    """Logs pretty """

    TAG_WIDTH = 7  # Justification width for tags.

    class Cx:
        """A context manager that manages the indent of logs."""

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
            raise ValueError('`indent` must be at least 1.')

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

        indent = str(gray('|')) + ' ' * (self._indent - 1)
        indent = indent * self._nesting

        self._out(f'[{datetime.now()}]', tag, indent + str(text))

        return Pretty.Cx(self, tag, text)


class Style:
    """..."""

    def __init__(self, *codes: str):
        self.codes = codes

    def __str__(self) -> str:
        """..."""
        return ''.join(self.codes)

    def __call__(self, style_or_str: Union['Style', str]) -> Union['Style', 'StyledText']:
        """..."""

        if isinstance(style_or_str, Style):
            return Style(*self.codes, *style_or_str.codes)
        else:
            return StyledText(style_or_str, self)

    def __or__(self, style_or_str: Union['Style', str]) -> Union['Style', 'StyledText']:
        """..."""
        return self(style_or_str)


class StyledText:
    """..."""

    def __init__(self, raw: Any, style: Style, reset: bool = True):
        self.raw = str(raw)
        self.style = style
        self.reset = reset

    def __str__(self) -> str:
        """Applies the style to the text."""
        return str(self.style) + self.raw + (colorama.Style.RESET_ALL * self.reset)

    def map(self, f: Callable) -> 'StyledText':
        """Maps the underlying text with the provided function."""
        return StyledText(f(self.raw), self.style, self.reset)


styles = [
    red    := Style(colorama.Fore.RED),
    blue   := Style(colorama.Fore.BLUE),
    green  := Style(colorama.Fore.GREEN),
    yellow := Style(colorama.Fore.YELLOW),
    gray   := Style(colorama.Fore.LIGHTBLACK_EX),

    normal := Style(colorama.Style.NORMAL),
    bold   := Style(colorama.Style.BRIGHT),
    dim    := Style(colorama.Style.DIM),
]
"""A list of predefined styles."""


if __name__ == '__main__':
    log = Pretty()
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
