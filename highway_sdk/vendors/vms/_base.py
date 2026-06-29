"""VMS 厂商基础模块。

提供 VMS（可变情报板）设备协议的公共抽象，包括：
- VMSFrame: VMS 帧基类（带起始符/结束符）
"""

from pydantic import Field, field_validator

from highway_sdk.core.constants import ETX, STX
from highway_sdk.core.frame import BaseFrame


class VMSFrame(BaseFrame):
    """VMS 帧基类。

    在 BaseFrame 基础上增加了起始符和结束符的验证。

    Attributes:
        start: 帧起始符，默认为 STX (0x02)。
        end: 帧结束符，默认为 ETX (0x03)。
    """

    start: bytes = Field(default=STX, frozen=True, description="帧起始符")
    end: bytes = Field(default=ETX, frozen=True, description="帧结束符")

    @field_validator("start")
    @classmethod
    def ensure_start(cls, v: bytes) -> bytes:
        """验证起始符是否为 STX。"""
        if v != STX:
            raise ValueError("start must be STX")
        return v

    @field_validator("end")
    @classmethod
    def ensure_end(cls, v: bytes) -> bytes:
        """验证结束符是否为 ETX。"""
        if v != ETX:
            raise ValueError("end must be ETX")
        return v
