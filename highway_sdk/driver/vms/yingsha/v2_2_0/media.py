from abc import abstractmethod
import configparser
from enum import IntEnum, StrEnum
from ftplib import CRLF
import re
from typing import Any, List, Self
from pydantic import BaseModel, Field, PrivateAttr


# ==============================================================================
# 枚举类
# ==============================================================================
class ScreenInOutEnum(IntEnum):
    CLEAR = 0
    NORMAL = 1
    MOVE_LEFT = 4


class ColorEnum(StrEnum):
    RED = "255000000000"
    GREEN = "000255000000"
    YELLOW = "255255000000"
    BLACK = "000000000000"


class FontEnum(StrEnum):
    HEI_TI = "h"
    KAI_TI = "k"
    SONG_TI = "s"
    FANG_SONG = "f"
    LI_SHU = "g"


class FontSizeEnum(IntEnum):
    """目前支持16、24和32点阵的汉字显示

    Args:
        IntEnum (_type_): _description_
    """

    SIZE_16 = 16
    SIZE_24 = 24
    SIZE_32 = 32


class EscEnum(StrEnum):
    XY = "\\C"  # XY坐标
    BMP = "\\B"  # BMP图片
    FONT = "\\F"  # 字体
    TEXT_COLOR = "\\c"  # 文本颜色
    WORD_SPACE = "\\S"
    LF = "\\n"


# ==============================================================================
# 媒体类
# ==============================================================================
class _BaseMedia(BaseModel):
    """媒体基类"""

    x: int = Field(..., ge=0, le=999)
    y: int = Field(..., ge=0, le=999)


class _TextMedia(_BaseMedia):
    r"""媒体类

    当图形与文字混合显示时，应该在str的开始就定义图形文件的显示起点和文件名，
        如\C000000\B001，即使显示位置是(0, 0)，\C转移序列也不能省略

    Args:
        BaseModel (_type_): _description_
    """

    font: FontEnum
    font_size: FontSizeEnum
    word_space: int = Field(..., ge=0, le=99)
    text: str
    text_color: ColorEnum

    def __str__(self) -> str:
        media = f"{EscEnum.XY.value}{self.x:03d}{self.y:03d}"
        media += f"{EscEnum.FONT.value}{self.font.value}{self.font_size.value}"
        media += f"{EscEnum.TEXT_COLOR.value}{self.text_color}"
        media += f"{EscEnum.WORD_SPACE.value}{self.word_space:02d}"
        media += self.text

        return media


class _BMPMedia(_BaseMedia):
    file_name: str

    def __str__(self) -> str:
        media = f"{EscEnum.XY.value}{self.x:03d}{self.y:03d}"
        media += f"{EscEnum.BMP.value}{self.file_name}"
        return media


class _Item(BaseModel):
    duration: int = Field(ge=2, le=30000)
    screen_in: ScreenInOutEnum
    play_speed: int = Field(ge=0, le=49)
    _media_list: List[_BaseMedia] = PrivateAttr(default_factory=list)

    def __str__(self) -> str:
        r"""
            当图形与文字混合显示时，应该在str的开始就定义图形文件的显示起点和文件名，
            如\C000000\B001，即使显示位置是(0, 0)，\C转移序列也不能省略。
        Returns:
            str: _description_
        """
        item = f"{self.duration},{self.screen_in},{self.play_speed},"

        if not len(self._media_list) == 0:
            image_string = ""
            text_string = ""
            for media in self._media_list:
                if isinstance(media, _BMPMedia):
                    image_string += f"{media}"
                else:
                    text_string += f"{media}"
            item += f"{image_string}"
            item += f"{text_string}"

        return item


class _Play:
    _item_list: List[_Item] = PrivateAttr(default_factory=list)

    def __str__(self) -> str:
        play = "[PLAYLIST]"
        play += CRLF
        play += f"ITEM_NO={len(self._item_list)}"
        play += CRLF
        for i, item in enumerate(self._item_list):
            play += f"ITEM{i}={item}"
            play += CRLF
        play += "[END]"

        return play


# ==============================================================================
# 媒体构造类
# ==============================================================================
class _BaseMediaBuilder:
    def __init__(self) -> None:
        self.x: int = 0
        self.y: int = 0

    @abstractmethod
    def build(self) -> _BaseMedia:
        pass


class TextMediaBuilder(_BaseMediaBuilder):
    def __init__(self) -> None:
        super().__init__()
        self.font: str = FontEnum.HEI_TI.value
        self.font_size: int = FontSizeEnum.SIZE_16.value
        self.word_space: int = 0
        self.text: str = ""
        self.text_color: str = ColorEnum.RED.value

    def build(self) -> _TextMedia:
        return _TextMedia(**self.__dict__)


class BMPMediaBuilder(_BaseMediaBuilder):
    def __init__(self) -> None:
        super().__init__()
        self.file_name: str = ""

    def build(self) -> _BMPMedia:
        return _BMPMedia(**self.__dict__)


class ItemBuilder:
    def __init__(self) -> None:
        self.duration: int = 500
        self.screen_in: int = ScreenInOutEnum.NORMAL
        self.play_speed: int = 0
        self._media_list: List[_BaseMedia] = []

    def add_media_builder(self, media_builder: _BaseMediaBuilder) -> Self:
        self._media_list.append(media_builder.build())
        return self

    def build(self) -> _Item:
        item = _Item(**self.__dict__)
        item._media_list = self._media_list
        return item


class PlayBuilder:
    def __init__(self):
        self._item_list: List[_Item] = []

    def add_item_builder(self, item_builder: ItemBuilder) -> Self:
        self._item_list.append(item_builder.build())
        return self

    def build(self) -> _Play:
        play = _Play(**self.__dict__)
        play._item_list = self._item_list
        return play


# ==============================================================================
# 解析器
# ==============================================================================
class BaseParser:
    @classmethod
    @abstractmethod
    def parse(cls, data: str) -> Any:
        pass


class PlayParser(BaseParser):
    @classmethod
    def parse(cls, data: str) -> PlayBuilder:
        play_parser = configparser.ConfigParser()
        play_parser.read_string(data)
        section = "PLAYLIST"
        item_no = int(play_parser.get(section, "ITEM_NO"))
        play_builder = PlayBuilder()

        for i in range(item_no):
            option = f"ITEM{i}"
            item = play_parser.get(section, option)
            item_builder = ItemParser.parse(item)
            play_builder.add_item_builder(item_builder)

        return play_builder


class ItemParser(BaseParser):
    """播放项解析器

    Args:
        BaseParser (_type_): _description_
    """

    XY_PATTERN = re.compile(r"\\C[0-9]{6}")
    FONT_PATTERN = re.compile(r"\\F([a-zA-Z])(\d{2})(\d{2})")
    COLOR_PATTERN = re.compile(r"\\c(\d{12})")
    BMP_PATTERN = re.compile(r"\\B(\d{3})")
    WORD_SPACE_PATTERN = re.compile(r"\\S(\d{2})")

    @classmethod
    def parse(cls, data: str) -> Any:
        fields = data.split(",")
        item_builder = ItemBuilder()
        item_builder.duration = int(fields[0])
        item_builder.screen_in = int(fields[1])
        item_builder.play_speed = int(fields[2])

        media_list = [part for part in cls.XY_PATTERN.split(fields[3]) if part]

        for media in media_list:
            res = cls.BMP_PATTERN.search(media)
            if res:
                bmp_builder = BMPMediaBuilder()
                bmp_builder.file_name = res.group(1)
                item_builder.add_media_builder(bmp_builder)
            else:
                text_builder = TextMediaBuilder()
                res = cls.FONT_PATTERN.search(media)
                if res:
                    text_builder.font = res.group(1)
                    text_builder.font_size = int(res.group(2))
                    media = cls.FONT_PATTERN.sub("", media, count=1)

                res = cls.COLOR_PATTERN.search(media)
                if res:
                    text_builder.text_color = res.group(1)
                    media = cls.COLOR_PATTERN.sub("", media, count=1)

                res = cls.WORD_SPACE_PATTERN.search(media)
                if res:
                    text_builder.word_space = int(res.group(1))
                    media = cls.WORD_SPACE_PATTERN.sub("", media, count=1)

                text_builder.text = media

                item_builder.add_media_builder(text_builder)

        return item_builder
