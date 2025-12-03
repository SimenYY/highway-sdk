from abc import ABC, abstractmethod
from typing import Self


class BaseMessageChainParser(ABC):
    """报文解析器

    Notes:
        链式调用

    """

    def __init__(self) -> None:
        self._successor = None
    def set_successor(self, successor: Self):
        self._successor = successor

    @abstractmethod
    def parse(self, *args, **kwargs):
        pass

    def __or__(self, other):
        """
        Usage:
            chain = parser1 | parser2 | parser3

        Args:
            other (Self): _description_

        Raises:
            TypeError: _description_

        Returns:
            Self: _description_
        """
        if not isinstance(other, BaseMessageChainParser):
            raise TypeError("The successor must be an instance of BaseMessageParser")

        current = self

        while current._successor is not None:
            current = current._successor
        current._successor = other
        return self

    def __str__(self) -> str:
        parts = []
        current = self

        while current is not None:
            parts.append(current.__class__.__name__)
            current = current._successor

        return " --> ".join(parts)
