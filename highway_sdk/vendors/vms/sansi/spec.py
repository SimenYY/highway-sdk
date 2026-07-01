from enum import Enum
from typing import Self

from pydantic import Field, computed_field

from highway_sdk.core.exceptions import CrcValidationError
from highway_sdk.vendors.vms._base import VMSFrame, crc16_ccitt, escape_bytes

ENCODING = "gbk"


class What(Enum):
    """帧类型枚举"""

    GET_PLAY_ITEM = b"97"  # 获取当前内容
    UPLOAD_FILE = b"10"  # 上载文件，可直接更改当前播放表
    DOWNLOAD_FILE = b"09"  # 下载文件 代替获取当前列表
    PLAY_LIST = b"98"  # 播放播放表, 可不用
    SET_BRIGHTNESS = b"05"  # 设置当前显示亮度
    SET_BRIGHTNESS_MODE = b"04"  # 设置当前亮度调节方式
    GET_BRIGHTNESS_AND_MODE = b"06"  # 取当前显示亮度和调节方式


class ResultCode(Enum):
    """返回状态码"""

    SUCCESS = b"0"
    FAILED = b"1"


class Frame(VMSFrame):
    """帧格式

    帧格式：
        【帧头1B】【地址2B】【帧类型2B】【帧数据nB】【帧校验2B】【帧尾1B】

    注：
        1. 先转义，后校验
    """

    address: bytes = Field(default=b"00", min_length=2, max_length=2, frozen=True, description="帧地址")
    what: What | None = Field(default=None, description="帧类型，作为请求帧时存在，作为响应帧是不存在")
    data: bytes = Field(default=b"", description="帧数据")

    @computed_field
    @property
    def crc(self) -> bytes:
        if self.what is None:
            # 对于响应帧，校验范围是地址+数据
            return self.calc_crc(self.address + self.data)
        else:
            # 对于请求帧，校验范围是地址+帧类型+数据
            return self.calc_crc(self.address + self.what.value + self.data)

    def __bytes__(self) -> bytes:
        if self.what is None:
            raise ValueError("what is None")

        escaped = self.escape(self.address + self.what.value + self.data + self.crc)
        return self.start + escaped + self.end

    @classmethod
    def from_bytes(cls, message: bytes) -> Self:
        """解包(无帧类型)

        Args:
            message: 原始字节消息

        Returns:
            解析后的Frame对象

        Raises:
            CrcValidationError: CRC校验失败
        """
        start = message[:1]
        end = message[-1:]

        # 反转义
        unescaped = cls.escape(message[1:-1], reverse=True)

        # 解析fields
        address = unescaped[:2]
        data = unescaped[2:-2]
        crc = unescaped[-2:]

        frame = cls(start=start, address=address, what=None, data=data, end=end)

        if frame.crc != crc:
            raise CrcValidationError("crc check failed")

        return frame

    @classmethod
    def calc_crc(cls, payload: bytes) -> bytes:
        """计算CRC"""
        return crc16_ccitt(payload)

    @classmethod
    def escape(cls, payload: bytes, *, reverse: bool = False) -> bytes:
        """转义

        Args:
            payload: 要转义的字节
            reverse: 是否反转义，默认为False

        Returns:
            转义或反转义后的字节
        """
        return escape_bytes(payload, reverse=reverse)
