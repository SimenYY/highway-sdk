from enum import Enum
from functools import lru_cache
from typing import Self

from pydantic import Field, computed_field

from highway_sdk.core.exceptions import CrcValidationError
from highway_sdk.vendors.vms._base import VMSFrame, crc16_ccitt, escape_bytes

ENCODING = "gbk"


class ResultCode(Enum):
    """显科返回码"""

    SUCCESS = b"\x01"
    FAILLED = b"\x00"


class What(Enum):
    """显科指令码"""

    GET_STATUS = b"00"  # 查询设备通信状态
    UPLOAD_FILE = b"20"  # 发送文件内容
    DOWNLOAD_FILE = b"21"  # 下载文件内容
    SELECT_PLAY_LIST = b"22"  # 播放播放表
    GET_PLAY_LIST_NAME = b"23"  # 获取当前列表名称
    GET_PLAY_ITEM = b"24"  # 获取当前内容
    GET_BRIGHTNESS_AND_MODE = b"05"  # 获取当前亮度


class Esc(Enum):
    """显科转义字符"""

    LF = "\\N"


class Frame(VMSFrame):
    """
    显科数据帧格式：【帧头 1B】-【类型 2B】-【地址 2B】-【数据 nB】-【校验 2B】-【帧尾 1B】

    注：
    1. 校验范围：类型+地址+数据
    2. 校验完，发送再转义
    """

    what: What = Field(..., description="帧类型")
    data: bytes = Field(default=b"", description="帧数据")
    address: bytes = Field(default=b"00", min_length=2, max_length=2, frozen=True, description="帧地址")

    @computed_field
    @property
    def crc(self) -> bytes:
        return self.calc_crc(self.what.value + self.address + self.data)

    def __bytes__(self) -> bytes:
        payload = self.start
        payload += self.what.value
        payload += self.address
        payload += self.escape(self.data + self.crc)
        payload += self.end
        return payload

    @classmethod
    def from_bytes(cls, message: bytes) -> Self:
        start, end = message[:1], message[-1:]
        unescaped = cls.escape(message[1:-1], reverse=True)
        what, address, data, crc = (
            unescaped[:2],
            unescaped[2:4],
            unescaped[4:-2],
            unescaped[-2:],
        )

        frame = cls(start=start, what=What(what), address=address, data=data, end=end)

        if frame.crc != crc:
            raise CrcValidationError("crc check failed")

        return frame

    @classmethod
    @lru_cache
    def calc_crc(cls, payload: bytes) -> bytes:
        """CRC校验计算"""
        return crc16_ccitt(payload)

    @classmethod
    def escape(cls, payload: bytes, *, reverse: bool = False) -> bytes:
        """转义处理"""
        return escape_bytes(payload, reverse=reverse)
