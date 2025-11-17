from abc import ABC, abstractmethod
import configparser
from enum import Enum, StrEnum
from ftplib import CRLF
import re
from typing import Any, Self
from pydantic import BaseModel, Field


# ==============================================================================
# 枚举量
# ==============================================================================
class ColorEnum(str, Enum):
    RED = "255000000000"
    GREEN = "000255000000"
    YELLOW = "255255000000"
    BLACK = "000000000000"


class FontEnum(str, Enum):
    HEI_TI = "h"
    KAI_TI = "k"
    SONG_TI = "s"
    FANG_SONG = "f"


class TextSizeEnum(int, Enum):
    SIZE_16 = 1616
    SIZE_24 = 2424
    SIZE_32 = 3232
    SIZE_48 = 4848
    SIZE_64 = 6464


class EscEnum(StrEnum):
    """转移字符

    Args:
        StrEnum (_type_): _description_
    """

    LF = "\\A"
    XY = "\\C"  # 起始坐标
    BMP = "\\B"  # bmp
    PNG = "\\P"
    JPG = "\\J"
    GIF = "\\G"  # GIF信息
    FONT = "\\F"  # 字体
    FONT_COLOR = "\\T"  # 字符颜色
    BACKGROUND_COLOR = "\\K"  # 字符背景颜色
    WORD_SPACE = "\\M"  # 字间距
    TEXT = "\\W"


# ==============================================================================
# 媒体类
# ==============================================================================
class _Media(BaseModel):
    x: int = Field(..., ge=0, le=999)
    y: int = Field(..., ge=0, le=999)


class _Text(_Media):
    text_color: ColorEnum
    background_color: ColorEnum
    word_space: int = Field(..., ge=0, le=99)
    font: FontEnum
    text_size: TextSizeEnum
    text: str

    def __str__(self):
        protocol = (
            f"{EscEnum.XY.value}{self.x:03d}{self.y:03d}"
            f"{EscEnum.FONT.value}{self.font.value}{self.text_size.value}"
            f"{EscEnum.FONT_COLOR.value}{self.text_color.value}"
            f"{EscEnum.BACKGROUND_COLOR.value}{self.background_color.value}"
        )
        if self.word_space != 0:
            protocol += f"{EscEnum.WORD_SPACE.value}{self.word_space:02d}"

        protocol += f"{EscEnum.TEXT.value}{self.text}"
        return protocol


class _Bmp(_Media):
    bmp_file_name: str

    def __str__(self) -> str:
        protocol = f"{EscEnum.XY.value}{self.x:03d}{self.y:03d}{EscEnum.BMP.value}{self.bmp_file_name}"
        return protocol


class _Png(_Media):
    png_file_name: str

    def __str__(self) -> str:
        protocol = f"{EscEnum.XY.value}{self.x:03d}{self.y:03d}{EscEnum.PNG.value}{self.png_file_name}"
        return protocol


class _Jpg(_Media):
    jpg_file_name: str

    def __str__(self) -> str:
        protocol = f"{EscEnum.XY.value}{self.x:03d}{self.y:03d}{EscEnum.JPG.value}{self.jpg_file_name}"
        return protocol


class _Gif(_Media):
    gif_file_name: str

    def __str__(self) -> str:
        protocol = f"{EscEnum.XY.value}{self.x:03d}{self.y:03d}{EscEnum.GIF.value}{self.gif_file_name}"
        return protocol


# ==============================================================================
# 媒体构造类
# ==============================================================================
class MediaBuilder(ABC):
    def __init__(self):
        self.x: int = 0
        self.y: int = 0

    @abstractmethod
    def build(self) -> _Media:
        """建造函数
        :return:
        """


class TextBuilder(MediaBuilder):
    def __init__(self, text: str):
        super().__init__()

        # 文本
        self.text = text
        self.text_color: str = ColorEnum.YELLOW.value
        self.background_color: str = ColorEnum.BLACK.value
        # 字间距
        self.word_space: int = 0
        # 输入示例 h
        self.font: str = FontEnum.HEI_TI.value
        # 输入示例 16
        self.text_size: int = TextSizeEnum.SIZE_16.value

    def build(self) -> _Text:
        return _Text(**self.__dict__)


class BmpBuilder(MediaBuilder):
    def __init__(self, bmp_file_name: str):
        super().__init__()
        self.bmp_file_name = bmp_file_name

    def build(self) -> _Bmp:
        return _Bmp(**self.__dict__)


class JpgBuilder(MediaBuilder):
    def __init__(self, jpg_file_name: str):
        super().__init__()
        self.jpg_file_name = jpg_file_name

    def build(self) -> _Jpg:
        return _Jpg(**self.__dict__)


class PngBuilder(MediaBuilder):
    def __init__(self, png_file_name: str):
        super().__init__()
        self.png_file_name = png_file_name

    def build(self) -> _Png:
        return _Png(**self.__dict__)


class GifBuilder(MediaBuilder):
    def __init__(self, gif_file_name: str):
        super().__init__()
        self.gif_file_name = gif_file_name

    def build(self) -> _Gif:
        return _Gif(**self.__dict__)


# ==============================================================================
# 播放项类
# ==============================================================================
class _Item(BaseModel):
    media_list: list[_Media]
    duration: int = Field(..., ge=2, le=30000)
    screen_in: int = Field(..., ge=0, le=30)
    play_effect: int = Field(..., ge=0, le=15)
    screen_out: int = Field(..., ge=0, le=15)
    play_speed: int = Field(..., ge=0, le=49)

    def __str__(self) -> str:
        if not self.media_list:
            raise ValueError("media is empty")

        protocol = f"{self.duration},{self.screen_in},{self.play_effect},{self.screen_out},{self.play_speed},"
        for media in self.media_list:
            protocol += str(media)
        return protocol


class ItemBuilder:
    def __init__(self):
        self.media_list: list[_Media] = []
        # 单位是十分之一s
        self.duration: int = 100
        self.screen_in: int = 0
        self.play_effect: int = 0
        self.screen_out: int = 0
        self.play_speed: int = 0

    def add_media_builder(self, builder: MediaBuilder) -> Self:
        self.media_list.append(builder.build())
        return self
    
    def build(self) -> _Item:
        return _Item(**self.__dict__)


# ==============================================================================
# 播放表类
# ==============================================================================
class _Play(BaseModel):
    item_list: list[_Item]

    def __str__(self) -> str:
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
    def __init__(self):
        self.item_list: list[_Item] = []

    def add_item_builder(self, builder: ItemBuilder) -> Self:
        self.item_list.append(builder.build())
        return self

    def build(self) -> _Play:
        return _Play(**self.__dict__)


# ==============================================================================
# 解析器
# ==============================================================================
class BaseParser:
    @classmethod
    @abstractmethod
    def parse(cls, data: str) -> Any:
        pass


class PlayParser(BaseParser):
    """播放表解析器

    Args:
        BaseParser (_type_): _description_
    """

    @classmethod
    def parse(cls, data: str) -> PlayBuilder:
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
    """播放项解析器

    Args:
        BaseParser (_type_): _description_
    """

    @classmethod
    def parse(cls, data: str) -> ItemBuilder:
        fields = data.split(",")

        item_builder = ItemBuilder()
        item_builder.duration = int(fields[0])
        item_builder.screen_in = int(fields[1])
        item_builder.play_effect = int(fields[2])
        item_builder.screen_out = int(fields[3])
        item_builder.play_speed = int(fields[4])
        
        # 一般位置转义都在最前面
        media_list = [
            EscEnum.XY.value + part
            for part in fields[5].split(EscEnum.XY.value)
            if part
        ]
        for media in media_list:
            media_builder = cls.parse_media(media)
            item_builder.add_media_builder(media_builder)


        return item_builder

    @classmethod
    def parse_media(cls, data: str):
        if EscEnum.TEXT in data:
            return TextParser.parse(data)
        elif EscEnum.BMP in data:
            return BmpParser.parse(data)
        elif EscEnum.JPG in data:
            return JpgParser.parse(data)
        elif EscEnum.PNG in data:
            return PngParser.parse(data)
        elif EscEnum.GIF in data:
            return GifParser.parse(data)
        else:
            raise ValueError("unknown media type")


class MediaParser(BaseParser):
    """媒体解析器

    Args:
        BaseParser (_type_): _description_
    """

    XY_PATTERN = re.compile(r"\\C(\d{3})(\d{3})")


class TextParser(MediaParser):
    """文本解析器

    Args:
        BaseParser (_type_): _description_
    """

    COLOR_PATTERN = re.compile(r"\\T(\d{12})")
    BG_COLOR_PATTERN = re.compile(r"\\K(\d{12})")  # 背景颜色
    WORD_SPACE_PATTERN = re.compile(r"\\M(\d{2})")
    FONT_PATTERN = re.compile(r"\\F([a-zA-Z])(\d{4})")
    TEXT_PATTERN = re.compile(r"\\W(.+)")

    @classmethod
    def parse(cls, data: str) -> TextBuilder:
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
    """Bmp解析器

    Args:
        BaseParser (_type_): _description_

    Returns:
        _type_: _description_
    """

    BMP_PATTERN = re.compile(r"\\B(\d{3})")

    @classmethod
    def parse(cls, data: str) -> BmpBuilder:
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
    """png解析器

    Args:
        BaseParser (_type_): _description_
    """

    PNG_PATTERN = re.compile(r"\\P(\d{3})")

    @classmethod
    def parse(cls, data: str) -> PngBuilder:
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
    """jpg解析器

    Args:
        BaseParser (_type_): _description_
    """

    JPG_PATTERN = re.compile(r"\\J(\d{3})")

    @classmethod
    def parse(cls, data: str) -> JpgBuilder:
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
    """gif解析器

    Args:
        BaseParser (_type_): _description_
    """

    GIF_PATTERN = re.compile(r"\\G(\d{3})")

    @classmethod
    def parse(cls, data: str) -> GifBuilder:
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
