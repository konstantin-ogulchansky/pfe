from abc import ABCMeta, abstractmethod
from datetime import datetime
from enum import Enum
from types import TracebackType
from typing import Any, Type, Optional, Callable


class Log(metaclass=ABCMeta):
    """An interface of all loggers."""

    def debug(self, item: Any) -> 'Scope':
        """Logs ``item`` with the ``DEBUG`` level."""
        return self(Record(item, Level.DEBUG))

    def info(self, item: Any) -> 'Scope':
        """Logs ``item`` with the ``INFO`` level."""
        return self(Record(item, Level.INFO))

    def warn(self, item: Any) -> 'Scope':
        """Logs ``item`` with the ``WARN`` level."""
        return self(Record(item, Level.WARN))

    def error(self, item: Any) -> 'Scope':
        """Logs ``item`` with the ``ERROR`` level."""
        return self(Record(item, Level.ERROR))

    def fatal(self, item: Any) -> 'Scope':
        """Logs ``item`` with the ``FATAL`` level."""
        return self(Record(item, Level.FATAL))

    @abstractmethod
    def __call__(self, record: 'Record') -> 'Scope':
        """Logs the provided ``record``."""


class Level(Enum):
    """TODO."""

    DEBUG = 1
    INFO  = 2
    WARN  = 3
    ERROR = 4
    FATAL = 5


class Record:
    """A timestamped record to be logged.

    :param item: an item to log (any object that can be converted to ``str``).
    :param level: a level of the record (e.g., ``INFO``, ``WARN``, etc.).
    :param timestamp: a timestamp of the record (optional; ``datetime.now()``
                      is used if the parameter is not specified).
    """

    def __init__(self, item: Any, level: Level, timestamp: Optional[datetime] = None):
        self._item = item
        self._level = level
        self._timestamp = timestamp or datetime.now()

    @property
    def level(self) -> Level:
        """Returns the level to log with."""
        return self._level

    @property
    def item(self) -> Any:
        """Returns the item to log."""
        return self._item

    @property
    def timestamp(self) -> datetime:
        """Returns the timestamp of the record."""
        return self._timestamp

    def map(self, function: Callable) -> 'Record':
        """Returns a new ``Record`` with the mapped item.

        :param function: a function to map the item with.

        :return: a mapped ``Record``.
        """
        return Record(function(self._item), self._level, self._timestamp)

    def refreshed(self) -> 'Record':
        """Returns a new ``Record`` with a refreshed timestamp.

        :return: a refreshed ``Record``.
        """
        return Record(self._item, self._level)


class Scope(metaclass=ABCMeta):
    """Defines a scope of logs.

    For example, one could indent nested logs.
    Consider the following code.
    ::
        log = ...

        with log.info('Nesting.'):
            log.info('A.')
            log.warn('B.')

        log.info('Out.')

    This code could produce the following output.
    ::
        INFO Nesting.
        INFO     B.
        WARN     C.
        INFO Out.

    Refer to ``Pretty`` for a more advanced example.
    """

    @abstractmethod
    def __enter__(self):
        """The beginning of the scope."""

    @abstractmethod
    def __exit__(self,
                 type: Optional[Type[BaseException]],
                 exception: Optional[BaseException],
                 traceback: Optional[TracebackType]):
        """The ending of the scope."""
