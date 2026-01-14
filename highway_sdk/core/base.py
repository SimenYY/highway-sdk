from typing import Protocol

from pydantic import BaseModel


class BaseTags(BaseModel): ...


class BaseMessageParser(Protocol):
    @classmethod
    def parse(cls, message: bytes) -> BaseTags:
        """报文解析"""
        ...
