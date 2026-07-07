"""丰海厂商CMS协议规范模块。

该模块定义了丰海厂商CMS设备的通信协议规范，包括：
- 帧类型枚举（What）
- 返回状态码枚举（ResultCode）
- 帧数据结构（Frame）
- CRC校验和转义处理
"""

from enum import Enum, IntEnum, StrEnum
from typing import Self

from pydantic import BaseModel, Field, ValidationError as PydanticValidationError, computed_field

from highway_sdk.core.constants import ETX, STX
from highway_sdk.core.exceptions import CrcValidationError, FrameValidationError
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
            FrameValidationError: 数据验证失败。
            CrcValidationError: CRC校验失败。
        """
        if not message.startswith(STX) or not message.endswith(ETX):
            raise ValueError("消息格式无效：数据长度不足或内容不符合协议要求")

        unescaped = cls.escape(message[1:-1], reverse=True)
        address = unescaped[:2]
        what = unescaped[2:4]
        data = unescaped[4:-2]
        crc = unescaped[-2:]

        try:
            frame = cls(address=address, what=What(what), data=data)
        except PydanticValidationError as e:
            raise FrameValidationError(e) from e
        if frame.crc != crc:
            raise CrcValidationError("数据校验失败：接收到的数据可能在传输中被损坏，请检查通信线路")
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


# ============================================================================
# 播放列表内容构造（媒体模型）
# ============================================================================


class Color(StrEnum):
    """颜色枚举（12位十进制，RRGGBB + 6位补零）。"""

    RED = "255000000000"
    GREEN = "000255000000"
    YELLOW = "255255000000"
    BLACK = "000000000000"
    TRANSPARENT = "t"


class Font(StrEnum):
    """字体枚举。"""

    HEI_TI = "h"  # 黑体
    KAI_TI = "k"  # 楷体
    SONG_TI = "s"  # 宋体
    FANG_SONG = "f"  # 仿宋


class FontSize(IntEnum):
    """字号枚举（协议要求重复输出，如 16→1616）。"""

    _16 = 1616
    _24 = 2424
    _32 = 3232
    _48 = 4848
    _64 = 6464


class Esc(StrEnum):
    """协议转义字符枚举。"""

    XY = "\\C"  # 坐标
    BMP = "\\B"  # BMP图片
    PNG = "\\P"  # PNG图片
    JPG = "\\J"  # JPG图片
    GIF = "\\G"  # GIF动画
    FLC = "\\F"  # FLC动画
    FONT = "\\f"  # 字体
    FONT_COLOR = "\\c"  # 字符颜色
    FONT_SHADOW_COLOR = "\\s"  # 字体阴影颜色
    BACKGROUND_COLOR = "\\b"  # 字符背景颜色
    WORD_SPACE = "\\S"  # 字间距
    LF = "\\n"  # 换行


class BaseMedia(BaseModel):
    """媒体基类。

    Attributes:
        x: X坐标，范围0-999。
        y: Y坐标，范围0-999。
    """

    x: int = Field(..., ge=0, le=999)
    y: int = Field(..., ge=0, le=999)


class Text(BaseMedia):
    """文本媒体。

    Attributes:
        font: 字体类型。
        font_size: 字号。
        font_color: 字符颜色。
        background_color: 背景颜色。
        word_space: 字间距，范围0-99。
        text: 文本内容。
    """

    font: Font
    font_size: FontSize
    font_color: Color
    background_color: Color
    word_space: int = Field(default=0, ge=0, le=99)
    text: str

    def __str__(self) -> str:
        """将文本媒体转换为协议字符串。"""
        protocol = (
            f"{Esc.XY.value}{self.x:03d}{self.y:03d}"
            f"{Esc.FONT.value}{self.font.value}{self.font_size.value}"
            f"{Esc.FONT_COLOR.value}{self.font_color.value}"
            f"{Esc.BACKGROUND_COLOR.value}{self.background_color.value}"
        )
        if self.word_space != 0:
            protocol += f"{Esc.WORD_SPACE.value}{self.word_space:02d}"
        protocol += self.text
        return protocol


class Bmp(BaseMedia):
    """BMP图片媒体。"""

    bmp_file_name: str

    def __str__(self) -> str:
        return f"{Esc.XY.value}{self.x:03d}{self.y:03d}{Esc.BMP.value}{self.bmp_file_name}"


class Png(BaseMedia):
    """PNG图片媒体。"""

    png_file_name: str

    def __str__(self) -> str:
        return f"{Esc.XY.value}{self.x:03d}{self.y:03d}{Esc.PNG.value}{self.png_file_name}"


class Jpg(BaseMedia):
    """JPG图片媒体。"""

    jpg_file_name: str

    def __str__(self) -> str:
        return f"{Esc.XY.value}{self.x:03d}{self.y:03d}{Esc.JPG.value}{self.jpg_file_name}"


class Gif(BaseMedia):
    """GIF动画媒体。"""

    gif_file_name: str

    def __str__(self) -> str:
        return f"{Esc.XY.value}{self.x:03d}{self.y:03d}{Esc.GIF.value}{self.gif_file_name}"


class Flc(BaseMedia):
    """FLC动画媒体。"""

    flc_file_name: str

    def __str__(self) -> str:
        return f"{Esc.XY.value}{self.x:03d}{self.y:03d}{Esc.FLC.value}{self.flc_file_name}"


class Item(BaseModel):
    """播放项。

    Attributes:
        media_list: 媒体列表。
        duration: 停留时间，范围2-30000（单位：百分之一秒）。
        screen_in_mode: 入屏方式，范围0-30。
        play_speed: 播放速度，范围0-49。
    """

    media_list: list[BaseMedia]
    duration: int = Field(..., ge=2, le=30000)
    screen_in_mode: int = Field(default=1, ge=0, le=30)
    play_speed: int = Field(default=0, ge=0, le=49)

    def __str__(self) -> str:
        """将播放项转换为协议字符串。"""
        if not self.media_list:
            raise ValueError("播放项的媒体列表不能为空")
        media_str = "".join(str(media) for media in self.media_list)
        return f"{self.duration},{self.screen_in_mode},{self.play_speed},{media_str}"


class Play(BaseModel):
    """播放列表。

    Attributes:
        item_list: 播放项列表。
    """

    item_list: list[Item]

    def __str__(self) -> str:
        """将播放列表转换为协议字符串。"""
        if not self.item_list:
            raise ValueError("播放列表不能为空")
        protocol = "[playlist]\r\n"
        protocol += f"item_no={len(self.item_list)}\r\n"
        for i, item in enumerate(self.item_list):
            protocol += f"item{i}={item}\r\n"
        return protocol
