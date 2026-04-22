"""点明厂商媒体播放模块。

该模块定义了点明VMS设备的媒体播放相关类，包括：
- 颜色、字体、字号等枚举
- 媒体类（文本、图片等）
- 媒体建造器
- 播放项和播放列表建造器
- 播放列表解析器
"""

from enum import IntEnum, StrEnum
from ftplib import CRLF

from pydantic import BaseModel, Field


class Color(StrEnum):
    """颜色枚举。

    定义了支持的RGB颜色值，格式为12位十六进制数（RRGGBB）。
    """

    RED = "255000000000"
    GREEN = "000255000000"
    YELLOW = "255255000000"
    BLACK = "000000000000"


class Font(StrEnum):
    """字体枚举。

    定义了支持的字体类型。
    """

    HEI_TI = "h"
    KAI_TI = "k"
    SONG_TI = "s"
    FANG_SONG = "f"


class FontSize(IntEnum):
    """字号枚举。

    定义了支持的字号大小。
    """

    _16 = 1616
    _24 = 2424
    _32 = 3232
    _48 = 4848
    _64 = 6464


class Esc(StrEnum):
    """转义字符枚举。

    定义了协议中使用的各种转义字符。
    """

    LF = "\\A"
    XY = "\\C"
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

    定义了所有媒体类型的公共属性。

    Attributes:
        x: X坐标，范围0-999。
        y: Y坐标，范围0-999。
    """

    x: int = Field(..., ge=0, le=999)
    y: int = Field(..., ge=0, le=999)


class Text(BaseMedia):
    """文本媒体类。

    定义了文本显示的所有属性。

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

    def __str__(self):
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
    """BMP图片媒体类。

    Attributes:
        bmp_file_name: BMP文件名。
    """

    bmp_file_name: str

    def __str__(self) -> str:
        """将BMP媒体转换为协议字符串。"""
        protocol = f"{Esc.XY.value}{self.x:03d}{self.y:03d}{Esc.BMP.value}{self.bmp_file_name}"
        return protocol


class Png(BaseMedia):
    """PNG图片媒体类。

    Attributes:
        png_file_name: PNG文件名。
    """

    png_file_name: str

    def __str__(self) -> str:
        """将PNG媒体转换为协议字符串。"""
        protocol = f"{Esc.XY.value}{self.x:03d}{self.y:03d}{Esc.PNG.value}{self.png_file_name}"
        return protocol


class Jpg(BaseMedia):
    """JPG图片媒体类。

    Attributes:
        jpg_file_name: JPG文件名。
    """

    jpg_file_name: str

    def __str__(self) -> str:
        """将JPG媒体转换为协议字符串。"""
        protocol = f"{Esc.XY.value}{self.x:03d}{self.y:03d}{Esc.JPG.value}{self.jpg_file_name}"
        return protocol


class Gif(BaseMedia):
    """GIF图片媒体类。

    Attributes:
        gif_file_name: GIF文件名。
    """

    gif_file_name: str

    def __str__(self) -> str:
        """将GIF媒体转换为协议字符串。"""
        protocol = f"{Esc.XY.value}{self.x:03d}{self.y:03d}{Esc.GIF.value}{self.gif_file_name}"
        return protocol


class Item(BaseModel):
    """播放项类。

    定义了单个播放项的所有属性。

    Attributes:
        media_list: 媒体列表。
        duration: 停留时间，范围2-30000（单位：十分之一秒）。
        screen_in: 入屏方式，范围0-30。
        play_effect: 播放效果，范围0-15。
        screen_out: 出屏方式，范围0-15。
        play_speed: 播放速度，范围0-49。
    """

    media_list: list[BaseMedia]
    duration: int = Field(..., ge=2, le=30000)
    screen_in: int = Field(..., ge=0, le=30)
    play_effect: int = Field(..., ge=0, le=15)
    screen_out: int = Field(..., ge=0, le=15)
    play_speed: int = Field(..., ge=0, le=49)

    def __str__(self) -> str:
        """将播放项转换为协议字符串。

        Returns:
            str: 协议字符串。

        Raises:
            ValueError: 媒体列表为空时抛出。
        """
        if not self.media_list:
            raise ValueError("media is empty")

        protocol = f"{self.duration},{self.screen_in},{self.play_effect},{self.screen_out},{self.play_speed},"
        for media in self.media_list:
            protocol += str(media)
        return protocol


class Play(BaseModel):
    """播放列表类。

    定义了播放列表的所有属性。

    Attributes:
        item_list: 播放项列表。
    """

    item_list: list[Item]

    def __str__(self) -> str:
        """将播放列表转换为协议字符串。

        Returns:
            str: 协议字符串。

        Raises:
            ValueError: 播放项列表为空时抛出。
        """
        if not self.item_list:
            raise ValueError("item_list is empty")

        protocol = "[PLAYLIST]"
        protocol += CRLF
        protocol += f"ITEM_NO={len(self.item_list):03d}"
        protocol += CRLF
        for i, item in enumerate(self.item_list):
            protocol += f"ITEM{i:03d}={item}"
            protocol += CRLF
        return protocol
