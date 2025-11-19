from abc import ABC, abstractmethod
import struct
from dataclasses import dataclass
from typing import Self

from loguru import Message
from highway_sdk.core.exceptions import CrcValidationError


@dataclass(frozen=True)
class SanSiCode:
    SUCCESS: bytes = b"\x30"
    FAILURE: bytes = b"\x31"


@dataclass(frozen=True)
class SanSiWhat:
    GET_ITEM = b"97"  # 获取当前内容

    UPLOAD_FILE = b"10"  # 上载文件，可直接更改当前播放表

    DOWNLOAD_FILE = b"09"  # 下载文件 代替获取当前列表

    PLAY_LIST = b"98"  # 播放播放表, 可不用

    SET_BRIGHTNESS = b"05"  # 设置当前显示亮度

    GET_BRIGHTNESS = b"06"  # 取当前显示亮度和调节方式


class SanSiEscape:
    """
    对发送报文，接受报文进行转义
    """

    def __init__(self, payload: bytes) -> None:
        self._payload: bytes = payload

    def byte_to_short(self) -> bytes:
        escaped = self._payload
        escaped = escaped.replace(b"\x1b", b"\x1b\x00")
        escaped = escaped.replace(b"\x02", b"\x1b\xe7")
        escaped = escaped.replace(b"\x03", b"\x1b\xe8")

        return escaped

    def short_to_byte(self) -> bytes:
        escaped = self._payload
        escaped = escaped.replace(b"\x1b\xe7", b"\x02")
        escaped = escaped.replace(b"\x1b\xe8", b"\x03")
        escaped = escaped.replace(b"\x1b\x00", b"\x1b")

        return escaped


@dataclass
class SanSiFrameResp:
    """
    帧格式：【帧头1B】【地址2B】【帧数据nB】【帧校验2B】【帧尾1B】
    注
    1. 先转义，后校验
    """

    data: bytes
    crc: bytes
    start: bytes = b"\x02"
    address: bytes = b"\x30\x30"
    end: bytes = b"\x03"

    @classmethod
    def unpack(cls, message: bytes) -> Self:
        """
        解包
        :param message:
        :raise CrcError
        :return:
        """
        data_crc = message[3:-1]
        escaped_data_crc = SanSiEscape(data_crc).short_to_byte()
        start = message[:1]
        end = message[-1:]
        address = message[1:3]
        crc = escaped_data_crc[-2:]
        data = escaped_data_crc[:-2]

        crc_16 = SanSiCRC(address + data).crc()
        if crc_16 != crc:
            raise CrcValidationError("crc check failed")

        return cls(start=start, address=address, data=data, crc=crc, end=end)


@dataclass
class SanSiFrameReq:
    """
    帧格式：【帧头1B】【地址2B】【帧类型2B】【帧数据nB】【帧校验2B】【帧尾1B】
    注
    1. 对地址，类型，数据进行校验
    2.先校验，后转义
    """

    what: bytes
    data: bytes
    crc: bytes
    start: bytes = b"\x02"
    address: bytes = b"\x30\x30"
    end: bytes = b"\x03"

    def __bytes__(self) -> bytes:
        escaped = SanSiEscape(self.data + self.crc).byte_to_short()
        return self.start + self.address + self.what + escaped + self.end

    @classmethod
    def pack(cls, what: bytes, data: bytes, **kwargs) -> Self:
        """打包
        :param what:
        :param data:
        :param kwargs:
        :return:
        """

        address = kwargs.get("address", cls.address)

        crc = SanSiCRC(address + what + data).crc()

        return cls(what=what, data=data, crc=crc, address=address)


class SanSiCRC:
    crc_table = [
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
        0xA3FB,
        0xB3DA,
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

    def __init__(self, payload: bytes) -> None:
        self._payload = payload

    def crc(self) -> bytes:
        crc = 0
        for i in range(len(self._payload)):
            crc = self.crc_table[((crc >> 8) ^ self._payload[i]) & 0xFF] ^ (crc << 8)
            # 强制让crc符合unsigned short类型
            crc = crc & 0xFFFF
        return struct.pack(">H", crc)


# ==============================================================================
# Message
# ==============================================================================
class MessageBuilder(ABC):
    encoding: str = "gbk"
    what: bytes

    @abstractmethod
    def build(self) -> SanSiFrameReq:
        pass


class SanSiMessageFactory:
    _registry: dict[bytes, type[MessageBuilder]] = {}

    @classmethod
    def register(cls, builder_class: type[MessageBuilder]):
        """类装饰器，注册消息构造器类

        Args:
            what (bytes): _description_
        """

        if not issubclass(builder_class, MessageBuilder):
            raise TypeError(f"{builder_class} must inherit from MessageBuilder")
        cls._registry[builder_class.what] = builder_class

        return builder_class

    @classmethod
    def create(cls, what: bytes, **kwargs):
        """创建消息"""
        if what not in cls._registry:
            raise ValueError(f"Unsupported message type: {what}")

        return cls._registry[what](**kwargs).build()


@SanSiMessageFactory.register
class MessageUploadFileBuilder(MessageBuilder):
    """上传文件

    Args:
        MessageBuilder (_type_): _description_

    Returns:
        _type_: _description_
    """

    what = SanSiWhat.UPLOAD_FILE

    def __init__(self, content: str, file_name: str = "play.lst") -> None:
        self.content = content
        self.file_name = file_name

    def build(self) -> SanSiFrameReq:
        data = self.file_name.encode(self.encoding, "ignore")
        data += b"\x2b"  # 分隔符，代表文件名结束
        data += b"\x00\x00\x00\x00"  # 文件指针偏移
        data += self.content.encode(self.encoding, "ignore")  # 文件内容

        return SanSiFrameReq.pack(self.what, data)


@SanSiMessageFactory.register
class MessageGetItemBuilder(MessageBuilder):
    """获取当前播放项

    Args:
        MessageBuilder (_type_): _description_
    """

    what = SanSiWhat.GET_ITEM

    def build(self) -> SanSiFrameReq:
        return SanSiFrameReq.pack(self.what, b"")


@SanSiMessageFactory.register
class MessageSetBrightnessBuilder(MessageBuilder):
    """设置亮度

    Args:
        MessageBuilder (_type_): _description_
    """

    what = SanSiWhat.SET_BRIGHTNESS

    def __init__(self, brightness: int) -> None:
        self.brightness = brightness

    def build(self) -> SanSiFrameReq:
        brightness = max(0, min(31, self.brightness))

        first = brightness // 10
        second = brightness % 10

        # 红，绿，蓝三基色相同
        data = b"".join([bytes([ord(str(first)), ord(str(second))])] * 3)
        return SanSiFrameReq.pack(self.what, data)


@SanSiMessageFactory.register
class MessageGetBrightnessBuilder(MessageBuilder):
    """获取亮度

    Args:
        MessageBuilder (_type_): _description_
    """

    what = SanSiWhat.GET_BRIGHTNESS

    def build(self) -> SanSiFrameReq:
        return SanSiFrameReq.pack(self.what, b"")


@SanSiMessageFactory.register
class MessageDownloadFileBuilder(MessageBuilder):
    """下载播放表，可以下载当前播放表

    Args:
        MessageBuilder (_type_): _description_
    """

    what = SanSiWhat.DOWNLOAD_FILE

    def __init__(self, file_name: str = "play.lst") -> None:
        self.file_name = file_name

    def build(self, **kwargs) -> SanSiFrameReq:
        data = self.file_name.encode(self.encoding)
        data += b"\x00\x00\x00\x00"  # 文件指针偏移
        return SanSiFrameReq.pack(self.what, data)
