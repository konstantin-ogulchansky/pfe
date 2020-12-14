from typing import Any, Union
from string import ascii_lowercase, ascii_uppercase

from pfe.misc.style import gray, StyledText, Style


def percents(current: int, total: int, precision: int = 1) -> str:
    """...

    An example.
    ::
        > print(percents(1, 2, precision=2))
         50.00%

        > print(percents(2, 2, precision=2))
        100.00%
    """

    justification = len('100.') + precision

    return f'{current / total * 100:>{justification}.{precision}f}%'


def itemize(title: Any, *items: Any, bullet: Union[str, StyledText] = gray | '-') -> str:
    """...

    An example.
    ::
        > print(itemize('Numbers:', *[1, 2, 3]))
        Numbers:
        - 1
        - 2
        - 3
    """

    list = (f'{bullet} {x}' for x in items)
    list = '\n'.join(list)

    return str(title) + '\n' + list


def enumerate(title: Any, *items: Any, bullet: Union[int, str, StyledText] = gray | '1') -> str:
    """...

    An example.
    ::
        > print(enumerate('Letters:', *'abc'))
        Letters:
        1. a
        2. b
        3. c
    """

    if isinstance(bullet, StyledText):
        bullets = bullet.raw
        style = bullet.style
    else:
        bullets = bullet
        style = Style()

    if bullets.isnumeric():
        bullets = range(int(bullets), int(bullets) + len(items))
    else:
        if len(bullets) != 1:
            raise ValueError(...)

        if bullets.islower():
            alphabet = ascii_lowercase
        else:
            alphabet = ascii_uppercase

        bullets = alphabet[alphabet.index(bullets):]

    list = (f'{style.apply(x)} {y}' for x, y in zip(bullets, items))
    list = '\n'.join(list)

    return str(title) + '\n' + list
