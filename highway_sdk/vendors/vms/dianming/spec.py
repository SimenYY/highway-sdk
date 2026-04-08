"""点明厂商VMS协议规范模块。

该模块定义了点明厂商VMS设备的通信协议规范，包括：
- 指令码枚举（What）
- 返回状态码枚举（ResultCode）
- 帧数据结构（Frame）
- CRC校验和转义处理
"""

from enum import Enum
from functools import lru_cache
from typing import Self

from pydantic import Field, computed_field

from highway_sdk.core.exceptions import CrcValidationError
from highway_sdk.vendors.vms._base import BaseFrame

ENCODING = "gbk"


class What(Enum):
    """指令码枚举。

    定义了点明VMS设备支持的所有指令类型，包括请求和响应。
    """

    GET_PLAY_ITEM_REQ = b"73"
    GET_PLAY_ITEM_RESP = b"74"

    GET_PLAY_LIST_REQ = b"57"
    GET_PLAY_LIST_RESP = b"58"

    SET_PLAY_LIST_AND_PLAY_REQ = b"71"
    SET_PLAY_LIST_AND_PLAY_RESP = b"72"

    DOWNLOAD_FILE_REQ = b"07"
    DOWNLOAD_FILE_RESP = b"08"

    GET_BRIGHTNESS_AND_MODE_REQ = b"21"
    GET_BRIGHTNESS_AND_MODE_RESP = b"22"

    SET_BRIGHTNESS_OR_MODE_REQ = b"23"
    SET_BRIGHTNESS_OR_MODE_RESP = b"24"


class ResultCode(Enum):
    """返回状态码枚举。

    定义了设备操作返回的状态码。
    """

    SUCCESS = b"1"
    FAILLED = b"0"


class Frame(BaseFrame):
    """点明VMS帧数据结构。

    帧格式：【起始符1B】【目的地址2B】【源地址2B】【控制码2B】【数据nB】【校验码2B】【结束符1B】

    注：
        1. 校验码校验范围：目的地址，源地址，控制码，数据
        2. 发送时先校验后转义，接受时先转义后校验

    Attributes:
        dst_addr: 目的地址，默认为"00"。
        src_addr: 源地址，默认为"01"。
        what: 控制码（指令类型）。
        data: 帧数据。
        crc: CRC校验码（计算字段）。
    """

    dst_addr: bytes = Field(
        default=b"\x30\x30",
        min_length=2,
        max_length=2,
        description="目的地址",
    )
    src_addr: bytes = Field(
        default=b"\x30\x31",
        min_length=2,
        max_length=2,
        description="源地址",
    )
    what: What = Field(..., description="控制码")
    data: bytes = Field(default=b"", description="帧数据")

    @computed_field
    @property
    def crc(self) -> bytes:
        """计算CRC校验码。"""
        return self.calc_crc(self.dst_addr + self.src_addr + self.what.value + self.data)

    def __bytes__(self) -> bytes:
        """将帧转换为字节数据。

        Returns:
            bytes: 转义后的完整帧数据。
        """
        return (
            self.start + self.escape(self.dst_addr + self.src_addr + self.what.value + self.data + self.crc) + self.end
        )

    @classmethod
    def from_bytes(cls, message: bytes) -> Self:
        """从字节数据解析帧。

        Args:
            message: 帧的字节数据。

        Returns:
            Self: 解析后的帧对象。

        Raises:
            CrcValidationError: CRC校验失败。
        """
        start, end = message[:1], message[-1:]
        unescaped = cls.escape(message[1:-1], reverse=True)
        dst_addr, src_addr, what, data, crc = (
            unescaped[:2],
            unescaped[2:4],
            unescaped[4:6],
            unescaped[6:-2],
            unescaped[-2:],
        )

        frame = cls(
            start=start,
            dst_addr=dst_addr,
            src_addr=src_addr,
            what=What(what),
            data=data,
            end=end,
        )
        if frame.crc != crc:
            raise CrcValidationError("crc check failed")
        return frame

    @classmethod
    @lru_cache
    def calc_crc(cls, payload: bytes) -> bytes:
        """计算CRC校验码。

        使用CRC-16-CCITT算法计算校验码。

        Args:
            payload: 需要校验的数据。

        Returns:
            bytes: 2字节的CRC校验码（大端序）。
        """
        crc = 0x0000
        for byte in payload:
            crc ^= byte << 8
            for _ in range(8):
                crc = (crc << 1) ^ 0x1021 if (crc & 0x8000) else (crc << 1)
                crc &= 0xFFFF
        return crc.to_bytes(2, "big")

    @classmethod
    def escape(cls, payload: bytes, *, reverse: bool = False) -> bytes:
        """转义处理。

        对特殊字符进行转义，避免与帧起始符和结束符冲突。

        Args:
            payload: 需要转义的数据。
            reverse: 是否反向转义（解析时使用）。

        Returns:
            bytes: 转义后的数据。

        转义规则：
            0x1B -> 0x1B 0x00
            0x02 -> 0x1B 0xE7
            0x03 -> 0x1B 0xE8
        """
        if reverse:
            payload = payload.replace(b"\x1b\xe7", b"\x02")
            payload = payload.replace(b"\x1b\xe8", b"\x03")
            payload = payload.replace(b"\x1b\x00", b"\x1b")
        else:
            payload = payload.replace(b"\x1b", b"\x1b\x00")
            payload = payload.replace(b"\x02", b"\x1b\xe7")
            payload = payload.replace(b"\x03", b"\x1b\xe8")
        return payload
