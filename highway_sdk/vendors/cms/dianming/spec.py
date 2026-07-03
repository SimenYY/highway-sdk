"""电明厂商CMS协议规范模块。

该模块定义了电明厂商CMS设备的通信协议规范，包括：
- 指令码枚举（What）
- 返回状态码枚举（ResultCode）
- 帧数据结构（Frame）
- CRC校验和转义处理
"""

from enum import Enum, IntEnum, StrEnum
from typing import Self

from pydantic import BaseModel, Field, computed_field

from highway_sdk.core.exceptions import CrcValidationError
from highway_sdk.vendors.cms._base import CMSFrame, crc16_ccitt, escape_bytes

ENCODING = "gbk"


class What(Enum):
    """指令码枚举。

    定义了电明CMS设备支持的所有指令类型，包括请求和响应。
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
    FAILED = b"0"


class Frame(CMSFrame):
    """电明CMS帧数据结构。

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
        default=b"01",
        min_length=2,
        max_length=2,
        description="目的地址",
    )
    src_addr: bytes = Field(
        default=b"01",
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
        return crc16_ccitt(self.dst_addr + self.src_addr + self.what.value + self.data)

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

        # 提取CRC（最后2字节）
        crc_received = unescaped[-2:]
        payload = unescaped[:-2]

        # 解析字段
        dst_addr = payload[:2]
        src_addr = payload[2:4]
        what = payload[4:6]
        data = payload[6:]

        frame = cls(
            start=start,
            dst_addr=dst_addr,
            src_addr=src_addr,
            what=What(what),
            data=data,
            end=end,
        )
        if frame.crc != crc_received:
            raise CrcValidationError(f"CRC check failed: expected {crc_received.hex()}, got {frame.crc.hex()}")
        return frame

    @staticmethod
    def escape(payload: bytes, *, reverse: bool = False) -> bytes:
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
        return escape_bytes(payload, reverse=reverse)


# ============================================================================
# 播放列表内容构造（媒体模型）
# ============================================================================


class Color(StrEnum):
    """颜色枚举。

    格式为12位十进制数（RRGGBB + 6位补零）。
    """

    RED = "255000000000"
    GREEN = "000255000000"
    YELLOW = "255255000000"
    BLACK = "000000000000"


class Font(StrEnum):
    """字体枚举。"""

    HEI_TI = "h"  # 黑体
    KAI_TI = "k"  # 楷体
    SONG_TI = "s"  # 宋体
    FANG_SONG = "f"  # 仿宋


class FontSize(IntEnum):
    """字号枚举。"""

    _16 = 1616
    _24 = 2424
    _32 = 3232
    _48 = 4848
    _64 = 6464


class Esc(StrEnum):
    """协议转义字符枚举。"""

    LF = "\\A"  # 换行
    XY = "\\C"  # 坐标
    BMP = "\\B"
    PNG = "\\P"
    JPG = "\\J"
    GIF = "\\G"
    FONT = "\\F"
    FONT_COLOR = "\\T"
    BACKGROUND_COLOR = "\\K"
    WORD_SPACE = "\\M"
    TEXT = "\\W"


class BaseMedia(BaseModel):
    """媒体基类。

    Attributes:
        x: X坐标，范围0-999。
        y: Y坐标，范围0-999。
    """

    x: int = Field(..., ge=0, le=999)
    y: int = Field(..., ge=0, le=999)


class Text(BaseMedia):
    """文本媒体类。

    Attributes:
        text_color: 文本颜色。
        background_color: 背景颜色。
        word_space: 字间距，范围0-99。
        font: 字体类型。
        text_size: 字号。
        text: 文本内容。
    """

    text_color: Color
    background_color: Color
    word_space: int = Field(..., ge=0, le=99)
    font: Font
    text_size: FontSize
    text: str

    def __str__(self) -> str:
        """将文本媒体转换为协议字符串。"""
        protocol = (
            f"{Esc.XY.value}{self.x:03d}{self.y:03d}"
            f"{Esc.FONT.value}{self.font.value}{self.text_size.value}"
            f"{Esc.FONT_COLOR.value}{self.text_color.value}"
            f"{Esc.BACKGROUND_COLOR.value}{self.background_color.value}"
        )
        if self.word_space != 0:
            protocol += f"{Esc.WORD_SPACE.value}{self.word_space:02d}"
        protocol += f"{Esc.TEXT.value}{self.text}"
        return protocol


class Bmp(BaseMedia):
    """BMP图片媒体类。"""

    bmp_file_name: str

    def __str__(self) -> str:
        return f"{Esc.XY.value}{self.x:03d}{self.y:03d}{Esc.BMP.value}{self.bmp_file_name}"


class Png(BaseMedia):
    """PNG图片媒体类。"""

    png_file_name: str

    def __str__(self) -> str:
        return f"{Esc.XY.value}{self.x:03d}{self.y:03d}{Esc.PNG.value}{self.png_file_name}"


class Jpg(BaseMedia):
    """JPG图片媒体类。"""

    jpg_file_name: str

    def __str__(self) -> str:
        return f"{Esc.XY.value}{self.x:03d}{self.y:03d}{Esc.JPG.value}{self.jpg_file_name}"


class Gif(BaseMedia):
    """GIF图片媒体类。"""

    gif_file_name: str

    def __str__(self) -> str:
        return f"{Esc.XY.value}{self.x:03d}{self.y:03d}{Esc.GIF.value}{self.gif_file_name}"


class Item(BaseModel):
    """播放项类。

    Attributes:
        media_list: 媒体列表。
        duration: 停留时间，范围2-30000（单位：十分之一秒）。
        screen_in_mode: 入屏方式，范围0-30。
        play_effect: 播放效果，范围0-15。
        screen_out_mode: 出屏方式，范围0-15。
        play_speed: 播放速度，范围0-49。
    """

    media_list: list[BaseMedia]
    duration: int = Field(..., ge=2, le=30000)
    screen_in_mode: int = Field(..., ge=0, le=30)
    play_effect: int = Field(..., ge=0, le=15)
    screen_out_mode: int = Field(..., ge=0, le=15)
    play_speed: int = Field(..., ge=0, le=49)

    def __str__(self) -> str:
        """将播放项转换为协议字符串。"""
        if not self.media_list:
            raise ValueError("media_list is empty")
        protocol = f"{self.duration},{self.screen_in_mode},{self.play_effect},{self.screen_out_mode},{self.play_speed},"
        for media in self.media_list:
            protocol += str(media)
        return protocol


class Play(BaseModel):
    """播放列表类。

    Attributes:
        item_list: 播放项列表。
    """

    item_list: list[Item]

    def __str__(self) -> str:
        """将播放列表转换为协议字符串。"""
        if not self.item_list:
            raise ValueError("item_list is empty")
        protocol = "[PLAYLIST]\r\n"
        protocol += f"ITEM_NO={len(self.item_list):03d}\r\n"
        for i, item in enumerate(self.item_list):
            protocol += f"ITEM{i:03d}={item}\r\n"
        return protocol
