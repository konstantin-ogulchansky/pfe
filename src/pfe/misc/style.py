"""
Provides `Style` and `StyledText` classes that allow
to combine ANSI style codes and apply them to text.
"""

from typing import Union, Any, Callable

import colorama


class Style:
    """An ANSI style.

    Examples.
    ::
        bold  = Style(colorama.Style.BRIGHT)
        red   = Style(colorama.Fore.RED)

        print(bold | red | 'text')

    :param codes: a tuple of ANSI codes (for example,
                  '\033[1m' for bright text).
    """

    def __init__(self, *codes: str):
        self.codes = codes

    def __str__(self) -> str:
        """Concatenates the codes."""
        return ''.join(self.codes)

    def combine(self, other: 'Style') -> 'Style':
        """Combines two styles.

        :param other: an instance of `Style`.

        :return: an instance of `Style` with the combined ANSI codes.
        """
        return Style(*self.codes, *other.codes)

    def apply(self, text: Any) -> 'StyledText':
        """Returns `StyledText` that applies the style to the provided text.

        :param text: text (or any object that can be converted to `str`)
                     to apply the style to.

        :return: an instance of `StyledText`.
        """
        return StyledText(text, self)

    def __call__(self, style_or_text: Union['Style', Any]) -> Union['Style', 'StyledText']:
        """Either combines two styles or applies a style to the provided text.

        :param style_or_text: either `Style` or text to apply the style to.

        :return: either `Style` or `StyledText`.
        """

        if isinstance(style_or_text, Style):
            return self.combine(style_or_text)
        else:
            return self.apply(style_or_text)

    def __or__(self, style_or_text: Union['Style', Any]) -> Union['Style', 'StyledText']:
        """An alias of `__call__` which sometimes looks better."""
        return self.__call__(style_or_text)


class StyledText:
    """Represents text styled with ANSI codes.

    :param raw: text (or any object that can be converted to `str`) to style.
    :param style: an instance of `Style`.
    :param reset: whether to reset the style after the text
                  (applies `colorama.Style.RESET_ALL` if enabled).
    """

    def __init__(self, raw: Any, style: Style, reset: bool = True):
        self.raw = str(raw)
        self.style = style
        self.reset = reset

    def __str__(self) -> str:
        """Applies the style to the text."""
        return str(self.style) + self.raw + (colorama.Style.RESET_ALL * self.reset)

    def map(self, f: Callable) -> 'StyledText':
        """Maps the underlying raw text with the provided function.

        :param f: a function to map the raw text with.

        :return: a new instance of `StyledText` with mapped text.
        """
        return StyledText(f(self.raw), self.style, self.reset)


def code(value: int) -> str:
    """Constructs an ANSI code with the provided `value`."""
    return '\033[' + str(value) + 'm'


styles = [
    red     := Style(colorama.Fore.RED),
    blue    := Style(colorama.Fore.BLUE),
    green   := Style(colorama.Fore.GREEN),
    yellow  := Style(colorama.Fore.YELLOW),
    magenta := Style(colorama.Fore.MAGENTA),
    cyan    := Style(colorama.Fore.CYAN),
    gray    := Style(colorama.Fore.LIGHTBLACK_EX),

    normal  := Style(colorama.Style.NORMAL),
    bold    := Style(colorama.Style.BRIGHT),
    dim     := Style(colorama.Style.DIM),

    # Some neat codes that are not supported by `colorama`,
    # but are handled properly by the terminal in PyCharm.
    italic     := Style(code(3)),
    underlined := Style(code(4)),
    strike     := Style(code(9)),
    framed     := Style(code(51)),
]
"""A list of predefined styles."""


if __name__ == '__main__':
    text: str = ' text '

    # Showing every style.
    print('Styles.')
    for style in styles:
        print('  -',
              repr(style.codes[0]).ljust(12),
              style.apply(text),
              colorama.Style.RESET_ALL)

    print()

    # Showing some examples of how styles can be combined.
    print('Examples.')
    print('  -', bold | red | text)
    print('  -', italic | green | text)
    print('  -', underlined | blue | text)
    print('  -', framed | magenta | text)
    print('  -', strike | cyan | text)
    print('  -', bold | italic | strike | framed | yellow | text)
