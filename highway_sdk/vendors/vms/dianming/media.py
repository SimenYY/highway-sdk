"""点明厂商媒体播放模块。

该模块定义了点明VMS设备的媒体播放相关类，包括：
- 颜色、字体、字号等枚举
- 媒体类（文本、图片等）
- 媒体建造器
- 播放项和播放列表建造器
- 播放列表解析器
"""

import configparser
import re
from abc import ABC, abstractmethod
from enum import Enum, StrEnum
from ftplib import CRLF
from typing import Any, Self

from pydantic import BaseModel, Field


class Color(str, Enum):
    """颜色枚举。

    定义了支持的RGB颜色值，格式为12位十六进制数（RRGGBB）。
    """

    RED = "255000000000"
    GREEN = "000255000000"
    YELLOW = "255255000000"
    BLACK = "000000000000"


class Font(str, Enum):
    """字体枚举。

    定义了支持的字体类型。
    """

    HEI_TI = "h"
    KAI_TI = "k"
    SONG_TI = "s"
    FANG_SONG = "f"


class FontSize(int, Enum):
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


class _Media(BaseModel):
    """媒体基类。

    定义了所有媒体类型的公共属性。

    Attributes:
        x: X坐标，范围0-999。
        y: Y坐标，范围0-999。
    """

    x: int = Field(..., ge=0, le=999)
    y: int = Field(..., ge=0, le=999)


class _Text(_Media):
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


class _Bmp(_Media):
    """BMP图片媒体类。

    Attributes:
        bmp_file_name: BMP文件名。
    """

    bmp_file_name: str

    def __str__(self) -> str:
        """将BMP媒体转换为协议字符串。"""
        protocol = f"{Esc.XY.value}{self.x:03d}{self.y:03d}{Esc.BMP.value}{self.bmp_file_name}"
        return protocol


class _Png(_Media):
    """PNG图片媒体类。

    Attributes:
        png_file_name: PNG文件名。
    """

    png_file_name: str

    def __str__(self) -> str:
        """将PNG媒体转换为协议字符串。"""
        protocol = f"{Esc.XY.value}{self.x:03d}{self.y:03d}{Esc.PNG.value}{self.png_file_name}"
        return protocol


class _Jpg(_Media):
    """JPG图片媒体类。

    Attributes:
        jpg_file_name: JPG文件名。
    """

    jpg_file_name: str

    def __str__(self) -> str:
        """将JPG媒体转换为协议字符串。"""
        protocol = f"{Esc.XY.value}{self.x:03d}{self.y:03d}{Esc.JPG.value}{self.jpg_file_name}"
        return protocol


class _Gif(_Media):
    """GIF图片媒体类。

    Attributes:
        gif_file_name: GIF文件名。
    """

    gif_file_name: str

    def __str__(self) -> str:
        """将GIF媒体转换为协议字符串。"""
        protocol = f"{Esc.XY.value}{self.x:03d}{self.y:03d}{Esc.GIF.value}{self.gif_file_name}"
        return protocol


class MediaBuilder(ABC):
    """媒体建造器抽象基类。

    定义了所有媒体建造器的公共接口。
    """

    def __init__(self):
        """初始化媒体建造器。"""
        self.x: int = 0
        self.y: int = 0

    @abstractmethod
    def build(self) -> _Media:
        """构建媒体对象。

        Returns:
            _Media: 构建完成的媒体对象。
        """
        ...


class TextBuilder(MediaBuilder):
    """文本媒体建造器。

    用于构建文本媒体对象。
    """

    def __init__(self, text: str):
        """初始化文本建造器。

        Args:
            text: 文本内容。
        """
        super().__init__()

        self.text = text
        self.text_color: str = Color.YELLOW.value
        self.background_color: str = Color.BLACK.value
        self.word_space: int = 0
        self.font: str = Font.HEI_TI.value
        self.text_size: int = FontSize._16.value

    def build(self) -> _Text:
        """构建文本媒体对象。

        Returns:
            _Text: 构建完成的文本媒体对象。
        """
        return _Text(**self.__dict__)


class BmpBuilder(MediaBuilder):
    """BMP图片媒体建造器。

    用于构建BMP图片媒体对象。
    """

    def __init__(self, bmp_file_name: str):
        """初始化BMP建造器。

        Args:
            bmp_file_name: BMP文件名。
        """
        super().__init__()
        self.bmp_file_name = bmp_file_name

    def build(self) -> _Bmp:
        """构建BMP媒体对象。

        Returns:
            _Bmp: 构建完成的BMP媒体对象。
        """
        return _Bmp(**self.__dict__)


class JpgBuilder(MediaBuilder):
    """JPG图片媒体建造器。

    用于构建JPG图片媒体对象。
    """

    def __init__(self, jpg_file_name: str):
        """初始化JPG建造器。

        Args:
            jpg_file_name: JPG文件名。
        """
        super().__init__()
        self.jpg_file_name = jpg_file_name

    def build(self) -> _Jpg:
        """构建JPG媒体对象。

        Returns:
            _Jpg: 构建完成的JPG媒体对象。
        """
        return _Jpg(**self.__dict__)


class PngBuilder(MediaBuilder):
    """PNG图片媒体建造器。

    用于构建PNG图片媒体对象。
    """

    def __init__(self, png_file_name: str):
        """初始化PNG建造器。

        Args:
            png_file_name: PNG文件名。
        """
        super().__init__()
        self.png_file_name = png_file_name

    def build(self) -> _Png:
        """构建PNG媒体对象。

        Returns:
            _Png: 构建完成的PNG媒体对象。
        """
        return _Png(**self.__dict__)


class GifBuilder(MediaBuilder):
    """GIF图片媒体建造器。

    用于构建GIF图片媒体对象。
    """

    def __init__(self, gif_file_name: str):
        """初始化GIF建造器。

        Args:
            gif_file_name: GIF文件名。
        """
        super().__init__()
        self.gif_file_name = gif_file_name

    def build(self) -> _Gif:
        """构建GIF媒体对象。

        Returns:
            _Gif: 构建完成的GIF媒体对象。
        """
        return _Gif(**self.__dict__)


class _Item(BaseModel):
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

    media_list: list[_Media]
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


class ItemBuilder:
    """播放项建造器。

    用于构建播放项对象。
    """

    def __init__(self):
        """初始化播放项建造器。"""
        self.media_list: list[_Media] = []
        self.duration: int = 100
        self.screen_in: int = 0
        self.play_effect: int = 0
        self.screen_out: int = 0
        self.play_speed: int = 0

    def add_media_builder(self, builder: MediaBuilder) -> Self:
        """添加媒体建造器。

        Args:
            builder: 媒体建造器。

        Returns:
            Self: 返回自身，支持链式调用。
        """
        self.media_list.append(builder.build())
        return self

    def build(self) -> _Item:
        """构建播放项对象。

        Returns:
            _Item: 构建完成的播放项对象。
        """
        return _Item(**self.__dict__)


class _Play(BaseModel):
    """播放列表类。

    定义了播放列表的所有属性。

    Attributes:
        item_list: 播放项列表。
    """

    item_list: list[_Item]

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


class PlayBuilder:
    """播放列表建造器。

    用于构建播放列表对象。
    """

    def __init__(self):
        """初始化播放列表建造器。"""
        self.item_list: list[_Item] = []

    def add_item_builder(self, builder: ItemBuilder) -> Self:
        """添加播放项建造器。

        Args:
            builder: 播放项建造器。

        Returns:
            Self: 返回自身，支持链式调用。
        """
        self.item_list.append(builder.build())
        return self

    def build(self) -> _Play:
        """构建播放列表对象。

        Returns:
            _Play: 构建完成的播放列表对象。
        """
        return _Play(**self.__dict__)


class BaseParser:
    """解析器抽象基类。

    定义了所有解析器的公共接口。
    """

    @classmethod
    @abstractmethod
    def parse(cls, data: str) -> Any:
        """解析数据。

        Args:
            data: 要解析的数据。

        Returns:
            Any: 解析结果。
        """
        ...


class PlayParser(BaseParser):
    """播放列表解析器。

    用于解析播放列表的协议字符串。
    """

    @classmethod
    def parse(cls, data: str) -> PlayBuilder:
        """解析播放列表。

        Args:
            data: 播放列表的协议字符串。

        Returns:
            PlayBuilder: 播放列表建造器。
        """
        play_builder = PlayBuilder()
        config_parser = configparser.ConfigParser()
        config_parser.read_string(data)
        item_no = config_parser.get("PLAYLIST", "ITEM_NO")
        count = int(item_no)
        for i in range(count):
            item = config_parser.get("PLAYLIST", f"ITEM{i:03d}")
            item_builder = ItemParser.parse(item)
            play_builder.add_item_builder(item_builder)

        return play_builder


class ItemParser(BaseParser):
    """播放项解析器。

    用于解析播放项的协议字符串。
    """

    @classmethod
    def parse(cls, data: str) -> ItemBuilder:
        """解析播放项。

        Args:
            data: 播放项的协议字符串。

        Returns:
            ItemBuilder: 播放项建造器。
        """
        fields = data.split(",")

        item_builder = ItemBuilder()
        item_builder.duration = int(fields[0])
        item_builder.screen_in = int(fields[1])
        item_builder.play_effect = int(fields[2])
        item_builder.screen_out = int(fields[3])
        item_builder.play_speed = int(fields[4])

        media_list = [Esc.XY.value + part for part in fields[5].split(Esc.XY.value) if part]
        for media in media_list:
            media_builder = cls.parse_media(media)
            item_builder.add_media_builder(media_builder)

        return item_builder

    @classmethod
    def parse_media(cls, data: str):
        """解析媒体数据。

        Args:
            data: 媒体的协议字符串。

        Returns:
            MediaBuilder: 媒体建造器。

        Raises:
            ValueError: 未知媒体类型时抛出。
        """
        if Esc.TEXT in data:
            return TextParser.parse(data)
        elif Esc.BMP in data:
            return BmpParser.parse(data)
        elif Esc.JPG in data:
            return JpgParser.parse(data)
        elif Esc.PNG in data:
            return PngParser.parse(data)
        elif Esc.GIF in data:
            return GifParser.parse(data)
        else:
            raise ValueError("unknown media type")


class MediaParser(BaseParser):
    """媒体解析器基类。

    定义了媒体解析器的公共属性和方法。
    """

    XY_PATTERN = re.compile(r"\\C(\d{3})(\d{3})")


class TextParser(MediaParser):
    """文本媒体解析器。

    用于解析文本媒体的协议字符串。
    """

    COLOR_PATTERN = re.compile(r"\\T(\d{12})")
    BG_COLOR_PATTERN = re.compile(r"\\K(\d{12})")
    WORD_SPACE_PATTERN = re.compile(r"\\M(\d{2})")
    FONT_PATTERN = re.compile(r"\\F([a-zA-Z])(\d{4})")
    TEXT_PATTERN = re.compile(r"\\W(.+)")

    @classmethod
    def parse(cls, data: str) -> TextBuilder:
        """解析文本媒体。

        Args:
            data: 文本媒体的协议字符串。

        Returns:
            TextBuilder: 文本媒体建造器。
        """
        text_builder = TextBuilder("")

        remaining = data

        res = cls.XY_PATTERN.search(remaining)
        if res:
            text_builder.x = int(res.group(1))
            text_builder.y = int(res.group(2))
            remaining = remaining.replace(res.group(0), "")

        res = cls.COLOR_PATTERN.search(remaining)
        if res:
            text_builder.text_color = res.group(1)
            remaining = remaining.replace(res.group(0), "")

        res = cls.BG_COLOR_PATTERN.search(remaining)
        if res:
            text_builder.background_color = res.group(1)
            remaining = remaining.replace(res.group(0), "")

        res = cls.WORD_SPACE_PATTERN.search(remaining)
        if res:
            text_builder.word_space = int(res.group(1))
            remaining = remaining.replace(res.group(0), "")

        res = cls.FONT_PATTERN.search(remaining)
        if res:
            text_builder.font = res.group(1)
            text_builder.text_size = int(res.group(2))
            remaining = remaining.replace(res.group(0), "")

        res = cls.TEXT_PATTERN.search(remaining)
        if res:
            text_builder.text = res.group(1)

        return text_builder


class BmpParser(MediaParser):
    """BMP图片媒体解析器。

    用于解析BMP图片媒体的协议字符串。
    """

    BMP_PATTERN = re.compile(r"\\B(\d{3})")

    @classmethod
    def parse(cls, data: str) -> BmpBuilder:
        """解析BMP媒体。

        Args:
            data: BMP媒体的协议字符串。

        Returns:
            BmpBuilder: BMP媒体建造器。
        """
        bmp_builder = BmpBuilder("")

        remaining = data

        res = cls.XY_PATTERN.search(remaining)
        if res:
            bmp_builder.x = int(res.group(1))
            bmp_builder.y = int(res.group(2))
            remaining = remaining.replace(res.group(0), "")

        res = cls.BMP_PATTERN.search(remaining)
        if res:
            bmp_builder.bmp_file_name = res.group(1)
            remaining = remaining.replace(res.group(0), "")

        return bmp_builder


class PngParser(MediaParser):
    """PNG图片媒体解析器。

    用于解析PNG图片媒体的协议字符串。
    """

    PNG_PATTERN = re.compile(r"\\P(\d{3})")

    @classmethod
    def parse(cls, data: str) -> PngBuilder:
        """解析PNG媒体。

        Args:
            data: PNG媒体的协议字符串。

        Returns:
            PngBuilder: PNG媒体建造器。
        """
        png_builder = PngBuilder("")

        remaining = data

        res = cls.XY_PATTERN.search(remaining)
        if res:
            png_builder.x = int(res.group(1))
            png_builder.y = int(res.group(2))
            remaining = remaining.replace(res.group(0), "")

        res = cls.PNG_PATTERN.search(remaining)
        if res:
            png_builder.png_file_name = res.group(1)
            remaining = remaining.replace(res.group(0), "")

        return png_builder


class JpgParser(MediaParser):
    """JPG图片媒体解析器。

    用于解析JPG图片媒体的协议字符串。
    """

    JPG_PATTERN = re.compile(r"\\J(\d{3})")

    @classmethod
    def parse(cls, data: str) -> JpgBuilder:
        """解析JPG媒体。

        Args:
            data: JPG媒体的协议字符串。

        Returns:
            JpgBuilder: JPG媒体建造器。
        """
        jpg_builder = JpgBuilder("")
        remaining = data
        res = cls.XY_PATTERN.search(remaining)
        if res:
            jpg_builder.x = int(res.group(1))
            jpg_builder.y = int(res.group(2))
            remaining = remaining.replace(res.group(0), "")
        res = cls.JPG_PATTERN.search(remaining)
        if res:
            jpg_builder.jpg_file_name = res.group(1)
            remaining = remaining.replace(res.group(0), "")

        return jpg_builder


class GifParser(MediaParser):
    """GIF图片媒体解析器。

    用于解析GIF图片媒体的协议字符串。
    """

    GIF_PATTERN = re.compile(r"\\G(\d{3})")

    @classmethod
    def parse(cls, data: str) -> GifBuilder:
        """解析GIF媒体。

        Args:
            data: GIF媒体的协议字符串。

        Returns:
            GifBuilder: GIF媒体建造器。
        """
        gif_builder = GifBuilder("")
        remaining = data
        res = cls.XY_PATTERN.search(remaining)
        if res:
            gif_builder.x = int(res.group(1))
            gif_builder.y = int(res.group(2))
            remaining = remaining.replace(res.group(0), "")
        res = cls.GIF_PATTERN.search(remaining)
        if res:
            gif_builder.gif_file_name = res.group(1)
            remaining = remaining.replace(res.group(0), "")

        return gif_builder
