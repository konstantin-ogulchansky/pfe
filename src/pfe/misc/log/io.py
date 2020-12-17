from contextlib import redirect_stdout, redirect_stderr
from io import StringIO
from typing import Any, Callable, ContextManager, IO


def suppress_stdout() -> ContextManager:
    """Suppresses the ``stdout`` stream."""
    return _redirect_io(redirect_stdout, lambda _: ...)


def suppress_stderr() -> ContextManager:
    """Suppresses the ``stderr`` stream."""
    return _redirect_io(redirect_stderr, lambda _: ...)


def redirect_stdout_to(log: Callable[[str], Any]) -> ContextManager:
    """Redirects the ``stdout`` stream to the provided log.

    :param log: a log function to redirect to.
    """
    return _redirect_io(redirect_stdout, log, enter=True)


def redirect_stderr_to(log: Callable[[str], Any]) -> ContextManager:
    """Redirects the ``stderr`` stream to the provided log.

    :param log: a log function to redirect to.
    """
    return _redirect_io(redirect_stderr, log, enter=True)


def _redirect_io(redirect: Callable[[IO], Any],
                 log: Callable[[str], Any],
                 enter: bool = False,
                 strip: bool = True) -> ContextManager:

    class IO(StringIO):
        """A wrapper around ``StringIO`` that emits
        events on ``write`` and ``writelines``."""

        def __init__(self, subscriber):
            super(IO, self).__init__()
            self._subscriber = subscriber

        def write(self, string):
            result = super(IO, self).write(string)
            self._subscriber(string.strip() if strip else string)
            return result

    class Cx:
        """..."""

        def __init__(self, cx):
            self._inner = cx
            self._inner.__enter__()

        def __enter__(self):
            # We need to skip the first `__enter__` since
            # we already entered once in `__init__`.
            self.__enter__ = self._inner.__enter__

        def __exit__(self, exc_type, exc_val, exc_tb):
            self._inner.__exit__(exc_type, exc_val, exc_tb)

    if enter:
        return Cx(redirect(IO(log)))
    else:
        return redirect(IO(log))


if __name__ == '__main__':
    import sys

    from pfe.misc.log.pretty import Pretty

    log = Pretty()

    # Written to the plain `stdout`.
    sys.stdout.write('[0]\n')

    with redirect_stdout_to(log.info):
        # Redirected to `log.info`.
        sys.stdout.writelines(['[1]', '[2]'])

        with redirect_stdout_to(log.debug):
            # Redirected to `log.debug`.
            sys.stdout.write('[3]')

        # Redirected to `log.info` again, since
        # we exited the previous context.
        sys.stdout.write('[4]')

    # Written to the plain `stdout` again.
    sys.stdout.write('[5]\n')

    with suppress_stdout(), suppress_stderr():
        sys.stdout.write('[*]')
        sys.stderr.write('[*]')

    # Redirected globally.
    redirect_stdout_to(log.info)
    redirect_stderr_to(log.warn)

    sys.stdout.write('[6]')
    sys.stderr.write('[7]')
