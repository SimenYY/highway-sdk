from abc import ABC
from dataclasses import dataclass, field
from typing import Any, ClassVar, Protocol

from highway_sdk.core.exceptions import ValidationError
from highway_sdk.core.spec import STX, ETX


class BaseMsgBuidler(Protocol):
    def build(self) -> Any: ...


@dataclass(slots=True)
class BaseVmsFrame:
    start: ClassVar[bytes] = STX
    end: ClassVar[bytes] = ETX

    crc: bytes = field(kw_only=True)

    @classmethod
    def validate_start_end(cls, message: bytes):
        if not message.startswith(STX) or not message.endswith(ETX):
            raise ValidationError("Invalid frame start/end")
