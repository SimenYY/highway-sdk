from enum import Enum, IntEnum, StrEnum
from typing import Self

from pydantic import BaseModel, Field, computed_field

from highway_sdk.core.exceptions import CrcValidationError
from highway_sdk.vendors.cms._base import CMSFrame, crc16_ccitt, escape_bytes

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


class Frame(CMSFrame):
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
            raise ValueError("帧类型未设置，无法将响应帧序列化为字节")

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
            raise CrcValidationError("数据校验失败：接收到的数据可能在传输中被损坏，请检查通信线路")

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
    MPG = "\\M"  # 视频文件
    FONT = "\\f"  # 字体
    FONT_COLOR = "\\c"  # 字符颜色
    BACKGROUND_COLOR = "\\b"  # 字符背景颜色
    WORD_SPACE = "\\S"  # 字间距


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


class Mpg(BaseMedia):
    """视频媒体。"""

    mpg_file_name: str

    def __str__(self) -> str:
        return f"{Esc.XY.value}{self.x:03d}{self.y:03d}{Esc.MPG.value}{self.mpg_file_name}"


class Item(BaseModel):
    """播放项。

    Attributes:
        media_list: 媒体列表。
        duration: 停留时间，范围2-30000（单位：百分之一秒）。
        screen_in: 入屏方式，范围0-30。
        play_speed: 播放速度，范围0-49。
    """

    media_list: list[BaseMedia]
    duration: int = Field(..., ge=2, le=30000)
    screen_in: int = Field(default=1, ge=0, le=30)
    play_speed: int = Field(default=0, ge=0, le=49)

    def __str__(self) -> str:
        """将播放项转换为协议字符串。"""
        if not self.media_list:
            raise ValueError("播放项的媒体列表不能为空")
        media_str = "".join(str(media) for media in self.media_list)
        return f"{self.duration},{self.screen_in},{self.play_speed},{media_str}"


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
