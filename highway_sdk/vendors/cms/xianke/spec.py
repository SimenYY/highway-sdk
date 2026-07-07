from enum import Enum, IntEnum, StrEnum
from typing import Self

from pydantic import BaseModel, Field, computed_field

from highway_sdk.core.exceptions import CrcValidationError
from highway_sdk.vendors.cms._base import CMSFrame, crc16_ccitt, escape_bytes

ENCODING = "gbk"


class ResultCode(Enum):
    """显科返回码"""

    SUCCESS = b"\x01"
    FAILED = b"\x00"


class What(Enum):
    """显科指令码"""

    GET_STATUS = b"00"  # 查询设备通信状态
    UPLOAD_FILE = b"20"  # 发送文件内容
    DOWNLOAD_FILE = b"21"  # 下载文件内容
    SELECT_PLAY_LIST = b"22"  # 播放播放表
    GET_PLAY_LIST_NAME = b"23"  # 获取当前列表名称
    GET_PLAY_ITEM = b"24"  # 获取当前内容
    GET_BRIGHTNESS_AND_MODE = b"05"  # 获取当前亮度


class Frame(CMSFrame):
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
            raise CrcValidationError("数据校验失败：接收到的数据可能在传输中被损坏，请检查通信线路")

        return frame

    @classmethod
    def calc_crc(cls, payload: bytes) -> bytes:
        """CRC校验计算"""
        return crc16_ccitt(payload)

    @classmethod
    def escape(cls, payload: bytes, *, reverse: bool = False) -> bytes:
        """转义处理"""
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


class Font(StrEnum):
    """字体枚举。"""

    HEI_TI = "h"  # 黑体
    KAI_TI = "k"  # 楷体
    SONG_TI = "s"  # 宋体
    FANG_SONG = "f"  # 仿宋


class FontSize(IntEnum):
    """字号枚举（2位数字）。"""

    _16 = 16
    _24 = 24
    _32 = 32
    _48 = 48
    _64 = 64


class ScreenInOut(IntEnum):
    """出入屏方式枚举。"""

    NORMAL = 1
    MOVE_UP = 6
    MOVE_DOWN = 7
    MOVE_LEFT = 8
    MOVE_RIGHT = 9


class Esc(StrEnum):
    """协议转义字符枚举。"""

    XY = "\\C"  # 坐标
    IMAGE = "\\I"  # 图片信息（默认bmp）
    ICON = "\\A"  # 交通图标
    FONT = "\\F"  # 字体
    FONT_COLOR = "\\T"  # 字符颜色
    BACKGROUND_COLOR = "\\B"  # 字符背景颜色
    TEXT = "\\U"  # 显示信息内容
    GIF = "\\G"  # GIF信息
    VIDEO = "\\V"  # Video信息
    LF = "\\N"  # 换行转义字符


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
        text: 文本内容。
    """

    font: Font
    font_size: FontSize
    font_color: Color
    background_color: Color
    text: str

    def __str__(self) -> str:
        """将文本媒体转换为协议字符串。"""
        return (
            f"{Esc.XY.value}{self.x:03d}{self.y:03d}"
            f"{Esc.FONT.value}{self.font.value}{self.font_size:02d}"
            f"{Esc.FONT_COLOR.value}{self.font_color.value}"
            f"{Esc.BACKGROUND_COLOR.value}{self.background_color.value}"
            f"{Esc.TEXT.value}{self.text}"
        )


class Image(BaseMedia):
    """图片媒体（BMP/GIF/Video 统一用 \\I 指令）。"""

    image_file_name: str

    def __str__(self) -> str:
        return f"{Esc.XY.value}{self.x:03d}{self.y:03d}{Esc.IMAGE.value}{self.image_file_name.rjust(3, '0')}"


class Gif(BaseMedia):
    """GIF动画媒体。"""

    gif_file_name: str

    def __str__(self) -> str:
        return f"{Esc.XY.value}{self.x:03d}{self.y:03d}{Esc.GIF.value}{self.gif_file_name.rjust(3, '0')}"


class Video(BaseMedia):
    """视频媒体。"""

    video_file_name: str

    def __str__(self) -> str:
        return f"{Esc.XY.value}{self.x:03d}{self.y:03d}{Esc.VIDEO.value}{self.video_file_name.rjust(3, '0')}"


class Item(BaseModel):
    """播放项。

    Attributes:
        media_list: 媒体列表。
        duration: 停留时间（单位：秒）。
        screen_in: 入屏方式。
        play_effect: 播放效果。
        screen_out: 出屏方式。
        play_speed: 播放速度。
    """

    media_list: list[BaseMedia]
    duration: int = Field(..., ge=1, le=65535)
    screen_in: ScreenInOut = Field(default=ScreenInOut.NORMAL)
    play_effect: int = Field(default=0, ge=0, le=15)
    screen_out: ScreenInOut = Field(default=ScreenInOut.NORMAL)
    play_speed: int = Field(default=1, ge=1, le=99)

    def __str__(self) -> str:
        """将播放项转换为协议字符串。"""
        if not self.media_list:
            raise ValueError("播放项的媒体列表不能为空")
        media_str = "".join(str(media) for media in self.media_list)
        return (
            f"{self.duration},"
            f"{self.screen_in.value},"
            f"{self.play_effect},"
            f"{self.screen_out.value},"
            f"{self.play_speed},"
            f"{media_str}"
        )


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
        protocol = "[LIST]\r\n"
        protocol += f"ItemCount={len(self.item_list):03d}\r\n"
        for i, item in enumerate(self.item_list):
            protocol += f"Item{i:02d}={item}\r\n"
        return protocol
