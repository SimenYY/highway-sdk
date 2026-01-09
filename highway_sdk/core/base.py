from pydantic import BaseModel
from typing import Protocol


class BaseTags(BaseModel): ...


class BaseMessageParser(Protocol):
    @classmethod
    def parse(cls, message: bytes) -> BaseTags:
        """报文解析"""
        ...
