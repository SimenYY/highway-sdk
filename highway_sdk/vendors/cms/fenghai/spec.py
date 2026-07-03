"""丰海厂商CMS协议规范模块。

该模块定义了丰海厂商CMS设备的通信协议规范，包括：
- 帧类型枚举（What）
- 返回状态码枚举（ResultCode）
- 帧数据结构（Frame）
- CRC校验和转义处理
"""

from enum import Enum
from typing import Self

from pydantic import Field, ValidationError as PydanticValidationError, computed_field

from highway_sdk.core.constants import ETX, STX
from highway_sdk.core.exceptions import CrcValidationError, ValidationError
from highway_sdk.vendors.cms._base import CMSFrame, escape_bytes

ENCODING = "gbk"


class What(Enum):
    """帧类型枚举。

    定义了丰海CMS设备支持的所有帧类型。
    """

    GET_PLAY_ITEM = b"97"
    UPLOAD_FILE = b"10"
    DOWNLOAD_FILE = b"09"
    PLAY_LIST = b"98"
    SET_BRIGHTNESS = b"05"
    SET_BRIGHTNESS_MODE = b"04"
    GET_BRIGHTNESS_AND_MODE = b"06"
    GET_SETTINGS = b"51"


class ResultCode(Enum):
    """返回状态码枚举。

    定义了设备操作返回的状态码。
    """

    SUCCESS = b"0"
    FAILED = b"1"


class Frame(CMSFrame):
    """丰海CMS帧数据结构。

    Attributes:
        address: 帧地址，默认为"00"。
        what: 帧类型。
        data: 帧数据。
        crc: CRC校验码（计算字段）。
    """

    address: bytes = Field(
        default=b"\x00\x00",
        min_length=2,
        max_length=2,
        description="帧地址",
    )
    what: What = Field(..., description="帧类型")
    data: bytes = Field(default=b"", description="帧数据")

    @computed_field
    @property
    def crc(self) -> bytes:
        """计算CRC校验码。"""
        return self.calc_crc(self.address + self.what.value + self.data)

    def __bytes__(self) -> bytes:
        """将帧转换为字节数据。

        Returns:
            bytes: 转义后的完整帧数据。
        """
        return self.start + self.escape(self.address + self.what.value + self.data + self.crc) + self.end

    @classmethod
    def from_bytes(cls, message: bytes) -> Self:
        """从字节数据解析帧。

        Args:
            message: 帧的字节数据。

        Returns:
            Self: 解析后的帧对象。

        Raises:
            ValueError: 消息格式无效。
            ValidationError: 数据验证失败。
            CrcValidationError: CRC校验失败。
        """
        if not message.startswith(STX) or not message.endswith(ETX):
            raise ValueError("invalid message")

        unescaped = cls.escape(message[1:-1], reverse=True)
        address = unescaped[:2]
        what = unescaped[2:4]
        data = unescaped[4:-2]
        crc = unescaped[-2:]

        try:
            frame = cls(address=address, what=What(what), data=data)
        except PydanticValidationError as e:
            raise ValidationError(e) from e
        if frame.crc != crc:
            raise CrcValidationError("crc check failed")
        return frame

    @classmethod
    def calc_crc(cls, payload: bytes):
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
        """
        return escape_bytes(payload, reverse=reverse)
