from enum import Enum
from functools import lru_cache
from typing import Self

from pydantic import Field, computed_field

from highway_sdk.core.constants import ESC, ETX, STX
from highway_sdk.core.exceptions import CrcValidationError
from highway_sdk.vendors.vms._base import BaseFrame

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
    FAILLED = b"1"


class Frame(BaseFrame):
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
    @lru_cache
    def calc_crc(cls, payload: bytes) -> bytes:
        """计算CRC"""
        CRC_TABLE = [
            0x0000,
            0x1021,
            0x2042,
            0x3063,
            0x4084,
            0x50A5,
            0x60C6,
            0x70E7,
            0x8108,
            0x9129,
            0xA14A,
            0xB16B,
            0xC18C,
            0xD1AD,
            0xE1CE,
            0xF1EF,
            0x1231,
            0x0210,
            0x3273,
            0x2252,
            0x52B5,
            0x4294,
            0x72F7,
            0x62D6,
            0x9339,
            0x8318,
            0xB37B,
            0xA35A,
            0xD3BD,
            0xC39C,
            0xF3FF,
            0xE3DE,
            0x2462,
            0x3443,
            0x0420,
            0x1401,
            0x64E6,
            0x74C7,
            0x44A4,
            0x5485,
            0xA56A,
            0xB54B,
            0x8528,
            0x9509,
            0xE5EE,
            0xF5CF,
            0xC5AC,
            0xD58D,
            0x3653,
            0x2672,
            0x1611,
            0x0630,
            0x76D7,
            0x66F6,
            0x5695,
            0x46B4,
            0xB75B,
            0xA77A,
            0x9719,
            0x8738,
            0xF7DF,
            0xE7FE,
            0xD79D,
            0xC7BC,
            0x48C4,
            0x58E5,
            0x6886,
            0x78A7,
            0x0840,
            0x1861,
            0x2802,
            0x3823,
            0xC9CC,
            0xD9ED,
            0xE98E,
            0xF9AF,
            0x8948,
            0x9969,
            0xA90A,
            0xB92B,
            0x5AF5,
            0x4AD4,
            0x7AB7,
            0x6A96,
            0x1A71,
            0x0A50,
            0x3A33,
            0x2A12,
            0xDBFD,
            0xCBDC,
            0xFBBF,
            0xEB9E,
            0x9B79,
            0x8B58,
            0xBB3B,
            0xAB1A,
            0x6CA6,
            0x7C87,
            0x4CE4,
            0x5CC5,
            0x2C22,
            0x3C03,
            0x0C60,
            0x1C41,
            0xEDAE,
            0xFD8F,
            0xCDEC,
            0xDDCD,
            0xAD2A,
            0xBD0B,
            0x8D68,
            0x9D49,
            0x7E97,
            0x6EB6,
            0x5ED5,
            0x4EF4,
            0x3E13,
            0x2E32,
            0x1E51,
            0x0E70,
            0xFF9F,
            0xEFBE,
            0xDFDD,
            0xCFFC,
            0xBF1B,
            0xAF3A,
            0x9F59,
            0x8F78,
            0x9188,
            0x81A9,
            0xB1CA,
            0xA1EB,
            0xD10C,
            0xC12D,
            0xF14E,
            0xE16F,
            0x1080,
            0x00A1,
            0x30C2,
            0x20E3,
            0x5004,
            0x4025,
            0x7046,
            0x6067,
            0x83B9,
            0x9398,
            0xB3FB,
            0xA3DA,
            0xC33D,
            0xD31C,
            0xE37F,
            0xF35E,
            0x02B1,
            0x1290,
            0x22F3,
            0x32D2,
            0x4235,
            0x5214,
            0x6277,
            0x7256,
            0xB5EA,
            0xA5CB,
            0x95A8,
            0x8589,
            0xF56E,
            0xE54F,
            0xD52C,
            0xC50D,
            0x34E2,
            0x24C3,
            0x14A0,
            0x0481,
            0x7466,
            0x6447,
            0x5424,
            0x4405,
            0xA7DB,
            0xB7FA,
            0x8799,
            0x97B8,
            0xE75F,
            0xF77E,
            0xC71D,
            0xD73C,
            0x26D3,
            0x36F2,
            0x0691,
            0x16B0,
            0x6657,
            0x7676,
            0x4615,
            0x5634,
            0xD94C,
            0xC96D,
            0xF90E,
            0xE92F,
            0x99C8,
            0x89E9,
            0xB98A,
            0xA9AB,
            0x5844,
            0x4865,
            0x7806,
            0x6827,
            0x18C0,
            0x08E1,
            0x3882,
            0x28A3,
            0xCB7D,
            0xDB5C,
            0xEB3F,
            0xFB1E,
            0x8BF9,
            0x9BD8,
            0xABBB,
            0xBB9A,
            0x4A75,
            0x5A54,
            0x6A37,
            0x7A16,
            0x0AF1,
            0x1AD0,
            0x2AB3,
            0x3A92,
            0xFD2E,
            0xED0F,
            0xDD6C,
            0xCD4D,
            0xBDAA,
            0xAD8B,
            0x9DE8,
            0x8DC9,
            0x7C26,
            0x6C07,
            0x5C64,
            0x4C45,
            0x3CA2,
            0x2C83,
            0x1CE0,
            0x0CC1,
            0xEF1F,
            0xFF3E,
            0xCF5D,
            0xDF7C,
            0xAF9B,
            0xBFBA,
            0x8FD9,
            0x9FF8,
            0x6E17,
            0x7E36,
            0x4E55,
            0x5E74,
            0x2E93,
            0x3EB2,
            0x0ED1,
            0x1EF0,
        ]

        crc = 0
        for byte in payload:
            crc = CRC_TABLE[((crc >> 8) ^ byte) & 0xFF] ^ (crc << 8)
            crc &= 0xFFFF  # 保持16位

        return crc.to_bytes(2, "big")

    @classmethod
    def escape(cls, payload: bytes, *, reverse: bool = False) -> bytes:
        """转义

        Args:
            payload: 要转义的字节
            reverse: 是否反转义，默认为False

        Returns:
            转义或反转义后的字节
        """
        if reverse:
            # 反转义
            payload = payload.replace(b"\x1b\xe7", STX)
            payload = payload.replace(b"\x1b\xe8", ETX)
            payload = payload.replace(b"\x1b\x00", ESC)
        else:
            # 转义
            payload = payload.replace(ESC, b"\x1b\x00")
            payload = payload.replace(STX, b"\x1b\xe7")
            payload = payload.replace(ETX, b"\x1b\xe8")

        return payload
