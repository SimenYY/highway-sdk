from dataclasses import dataclass, asdict
import json
from typing import Any, Protocol


@dataclass
class BaseTags:
    def to_dict(self):
        return asdict(self)

    def __str__(self) -> str:
        return json.dumps(self.to_dict(), indent=4, ensure_ascii=False)


class BaseMessageParser(Protocol):
    @classmethod
    def parse(cls, message: bytes) -> BaseTags:
        """报文解析"""
        ...