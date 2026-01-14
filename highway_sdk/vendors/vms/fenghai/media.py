"""丰海厂商媒体播放模块。

该模块定义了丰海VMS设备的媒体播放相关类，包括：
- 入屏方式、颜色、字体、字号等枚举
- 媒体类（文本、BMP、FLC动画等）
- 播放项和播放列表类
"""

from enum import IntEnum, StrEnum
from ftplib import CRLF

from pydantic import BaseModel, Field


class ScreenInMode(IntEnum):
    """入屏方式枚举。

    定义了节目进入屏幕的方式。
    """

    CLEAR = 0
    NORMAL = 1


class Color(StrEnum):
    """颜色枚举。

    定义了支持的RGB颜色值，格式为12位十六进制数（RRGGBB）。
    """

    RED = "255000000000"
    GREEN = "000255000000"
    YELLOW = "255255000000"
    BLACK = "000000000000"
    TRANSPARENT = "t"


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

    _16 = 16
    _24 = 24
    _32 = 32
    _48 = 48
    _64 = 64


class Esc(StrEnum):
    """转义字符枚举。

    定义了协议中使用的各种转义字符。
    """

    XY = "\\C"
    BMP = "\\B"
    FLC = "\\F"
    FONT = "\\f"
    FONT_COLOR = "\\c"
    FONT_SHADOW_COLOR = "\\s"
    BACKGROUND_COLOR = "\\b"
    WORD_SPACE = "\\S"
    LF = "\\n"


class BaseMedia(BaseModel):
    """媒体基类。

    定义了所有媒体类型的公共属性。

    Attributes:
        x: 左上角X坐标，范围0-999。
        y: 左上角Y坐标，范围0-999。
    """

    x: int = Field(default=0, ge=0, le=999, description="左上角X坐标")
    y: int = Field(default=0, ge=0, le=999, description="左上角Y坐标")


class Text(BaseMedia):
    """文本媒体类。

    定义了文本显示的所有属性。

    Attributes:
        background_color: 背景颜色。
        font_shadow_color: 字体阴影颜色。
        word_space: 字间距，范围-9到99。
        font_color: 字体颜色。
        font: 字体类型。
        font_size: 字号。
        text: 显示文本。
    """

    background_color: Color | None = Field(default=None, description="背景颜色")
    font_shadow_color: Color | None = Field(default=None, description="字体阴影颜色")
    word_space: int | None = Field(default=None, ge=-9, le=99, description="字间距")
    font_color: Color = Field(..., description="字体颜色")
    font: Font = Field(..., description="字体")
    font_size: FontSize = Field(..., description="字体大小")
    text: str = Field(..., description="显示文本")

    def __str__(self):
        """将文本媒体转换为协议字符串。"""
        protocol = f"{Esc.XY.value}{self.x:03d}{self.y:03d}"

        if self.font_shadow_color:
            protocol += f"{Esc.FONT_SHADOW_COLOR.value}{self.font_shadow_color}"
        if self.background_color:
            protocol += f"{Esc.BACKGROUND_COLOR.value}{self.background_color.value}"
        if self.word_space:
            protocol += f"{Esc.WORD_SPACE.value}{self.word_space:02d}"
        protocol += f"{Esc.FONT.value}{self.font.value}"
        protocol += f"{self.font_size.value}{self.font_size.value}"
        protocol += f"{Esc.FONT_COLOR.value}{self.font_color.value}"
        protocol += f"{self.text}"

        return protocol


class Bmp(BaseMedia):
    """BMP图片媒体类。

    Attributes:
        bmp_file_name: BMP文件名。
    """

    bmp_file_name: str

    def __str__(self):
        """将BMP媒体转换为协议字符串。"""
        protocol = f"{Esc.XY.value}{self.x:03d}{self.y:03d}{Esc.BMP.value}{self.bmp_file_name}"
        return protocol


class Flc(BaseMedia):
    """FLC动画媒体类。

    Attributes:
        flc_file_name: FLC文件名。
    """

    flc_file_name: str

    def __str__(self):
        """将FLC媒体转换为协议字符串。"""
        protocol = f"{Esc.XY.value}{self.x:03d}{self.y:03d}{Esc.FLC.value}{self.flc_file_name}"
        return protocol


class Item(BaseModel):
    """播放项类。

    定义了单个播放项的所有属性。

    Attributes:
        media_list: 媒体列表。
        duration: 停留时间，范围2-30000（单位：百分之一秒）。
        screen_in_mode: 节目进入屏幕方式。
        play_speed: 播放速度，范围0-49。
    """

    media_list: list[BaseMedia] = Field(default_factory=list, description="媒体列表")
    duration: int = Field(default=1000, ge=2, le=30000, description="停留时间, 百分之一秒")
    screen_in_mode: ScreenInMode = Field(default=ScreenInMode.NORMAL, description="节目进入屏幕方式")
    play_speed: int = Field(default=0, ge=0, le=49, description="播放速度")

    def __str__(self):
        """将播放项转换为协议字符串。"""
        media_str = "".join(str(media) for media in self.media_list)
        protocol = f"{self.duration},{self.screen_in_mode},{self.play_speed},{media_str}"

        return protocol


class Play(BaseModel):
    """播放列表类。

    定义了播放列表的所有属性。

    Attributes:
        item_list: 播放项列表。
    """

    item_list: list[Item] = Field(default_factory=list, description="播放项列表")

    def __str__(self):
        """将播放列表转换为协议字符串。"""
        protocol = "[playlist]"
        protocol += CRLF
        protocol += f"item_no={len(self.item_list)}"
        protocol += CRLF
        for i, item_builder in enumerate(self.item_list):
            protocol += f"item{i}={item_builder}"
            protocol += CRLF

        return protocol
