from abc import ABCMeta, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any, Optional, Callable, Union, ContextManager


class Log(metaclass=ABCMeta):
    """An interface of all loggers."""

    class Scope(metaclass=ABCMeta):
        """Defines a scope of logs.

        Scopes can be used to visually indent log records
        in order to make them more readable and pretty.

        Consider the following code.
        ::
            log: Log = ...

            with log.scope.info('Opened.'):
                log.info('Nested.')

            log.info('Closed.')

        This code could produce the following output.
        ::
            INFO   Opened.
            INFO   |   Nested.
            INFO   Closed.

        Refer to ``Pretty`` for a more advanced example.
        """

        def debug(self, item: Any) -> ContextManager:
            """Logs ``item`` with the ``DEBUG`` level."""
            return self(Record(item, Level.DEBUG))

        def info(self, item: Any) -> ContextManager:
            """Logs ``item`` with the ``INFO`` level."""
            return self(Record(item, Level.INFO))

        def warn(self, item: Any) -> ContextManager:
            """Logs ``item`` with the ``WARN`` level."""
            return self(Record(item, Level.WARN))

        def error(self, item: Any) -> ContextManager:
            """Logs ``item`` with the ``ERROR`` level."""
            return self(Record(item, Level.ERROR))

        def fatal(self, item: Any) -> ContextManager:
            """Logs ``item`` with the ``FATAL`` level."""
            return self(Record(item, Level.FATAL))

        @abstractmethod
        def __call__(self, item: Union[Any, 'Record']) -> ContextManager:
            """TODO."""

    def debug(self, item: Any):
        """Logs ``item`` with the ``DEBUG`` level."""
        return self(Record(item, Level.DEBUG))

    def info(self, item: Any):
        """Logs ``item`` with the ``INFO`` level."""
        return self(Record(item, Level.INFO))

    def warn(self, item: Any):
        """Logs ``item`` with the ``WARN`` level."""
        return self(Record(item, Level.WARN))

    def error(self, item: Any):
        """Logs ``item`` with the ``ERROR`` level."""
        return self(Record(item, Level.ERROR))

    def fatal(self, item: Any):
        """Logs ``item`` with the ``FATAL`` level."""
        return self(Record(item, Level.FATAL))

    @abstractmethod
    def __call__(self, item: Union[Any, 'Record']):
        """Logs the provided ``item``."""

    @property
    @abstractmethod
    def scope(self) -> 'Log.Scope':
        """TODO."""


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
