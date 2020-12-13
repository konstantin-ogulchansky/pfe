from types import TracebackType
from typing import Type, Optional

from pfe.misc.log import core


class Nothing(core.Log):
    """Does nothing.

    This ``Log`` can be used in order to avoid checks for ``None``.
    For example,
    ::
        def something_interesting(log: Log = Nothing()):
            ...  # Do something.
            log.info('Blah.')
            log.info('Blah.')
            ...  # Do something else.

    The function ``something_interesting`` can be called without any
    arguments, and its ``log`` argument will default to ``Nothing()``.
    Thus, all calls to ``log`` will be ignored, and nothing will be
    logged.
    """

    def __call__(self, record: core.Record) -> core.Scope:
        """Does literally nothing and returns an empty ``Scope``."""
        return Scope()


class Scope(core.Scope):
    """An empty scope that does not do anything
    neither in ``__enter__`` nor in ``__exit__``"""

    def __enter__(self):
        pass

    def __exit__(self,
                 type: Optional[Type[BaseException]],
                 exception: Optional[BaseException],
                 traceback: TracebackType):
        pass


if __name__ == '__main__':
    # Nothing is logged.
    log = Nothing()
    log.debug('[1]')

    with log.error('[2]'):
        log.info('[3]')
        log.warn('[4]')
