from contextlib import nullcontext
from typing import Union, Any, ContextManager

from pfe.misc.log.core import Log, Record


class Nothing(Log):
    """Logs nothing.

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

    class Scope(Log.Scope):
        """An empty scope that does not do anything
        neither in ``__enter__`` nor in ``__exit__``"""

        def __call__(self, item: Union[Any, Record]) -> ContextManager:
            return nullcontext()

    @property
    def scope(self) -> Log.Scope:
        return Nothing.Scope()

    def __call__(self, item: Union[Any, Record]):
        """Does nothing."""


if __name__ == '__main__':
    # Nothing is logged.
    log = Nothing()
    log.debug('[1]')

    with log.scope.error('[2]'):
        log.info('[3]')
        log.warn('[4]')
