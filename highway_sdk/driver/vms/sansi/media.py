from abc import ABC, abstractmethod
from ftplib import CRLF
from pydantic import BaseModel, Field
from enum import StrEnum, IntEnum
from typing import List


# ==============================================================================
# 枚举类
# ==============================================================================
class ScreenInEnum(IntEnum):
    NORMAL = 1


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


class TextSizeEnum(IntEnum):
    SIZE_16 = 16
    SIZE_24 = 24
    SIZE_32 = 32
    SIZE_48 = 48
    SIZE_64 = 64


class EscEnum(StrEnum):
    XY = "\\C"  # 起始坐标
    BMP = "\\B"  # bmp
    PNG = "\\P"
    JPG = "\\J"
    GIF = "\\G"  # GIF信息
    MPG = "\\M"  # video信息
    FONT = "\\f"  # 字体
    FONT_COLOR = "\\c"  # 字符颜色
    BACKGROUND_COLOR = "\\b"  # 字符背景颜色
    WORD_SPACE = "\\S"  # 字间距


# ==============================================================================
# 媒体类
# ==============================================================================
class Media(BaseModel):
    x: int = Field(..., ge=0, le=999)
    y: int = Field(..., ge=0, le=999)


class Text(Media):
    text_color: ColorEnum
    background_color: ColorEnum
    word_space: int = Field(..., ge=0, le=99)
    font: FontEnum
    text_size: TextSizeEnum
    text: str

    def __str__(self):
        protocol = (
            f"{EscEnum.XY.value}{self.x:03d}{self.y:03d}"
            f"{EscEnum.FONT.value}{self.font.value}{self.text_size.value}{self.text_size.value}"
            f"{EscEnum.FONT_COLOR.value}{self.text_color.value}"
            f"{EscEnum.BACKGROUND_COLOR.value}{self.background_color.value}"
            f"{EscEnum.WORD_SPACE.value}{self.word_space:02d}"
            f"{self.text}"
        )
        return protocol


class Bmp(Media):
    bmp_file_name: str

    def __str__(self):
        protocol = f"{EscEnum.XY.value}{self.x:03d}{self.y:03d}{EscEnum.BMP.value}{self.bmp_file_name}"
        return protocol


class Png(Media):
    png_file_name: str

    def __str__(self):
        protocol = f"{EscEnum.XY.value}{self.x:03d}{self.y:03d}{EscEnum.PNG.value}{self.png_file_name}"
        return protocol


class Jpg(Media):
    jpg_file_name: str

    def __str__(self):
        protocol = f"{EscEnum.XY.value}{self.x:03d}{self.y:03d}{EscEnum.JPG.value}{self.jpg_file_name}"
        return protocol


class Gif(Media):
    gif_file_name: str

    def __str__(self):
        protocol = f"{EscEnum.XY.value}{self.x:03d}{self.y:03d}{EscEnum.GIF.value}{self.gif_file_name}"
        return protocol


class Mpg(Media):
    """
    video
    """

    mpg_file_name: str

    def __str__(self):
        protocol = f"{EscEnum.XY.value}{self.x:03d}{self.y:03d}{EscEnum.MPG.value}{self.mpg_file_name}"
        return protocol


# ==============================================================================
# 媒体构造类
# ==============================================================================
class MediaBuilder(ABC):
    def __init__(self):
        self.x: int = 0
        self.y: int = 0

    @abstractmethod
    def build(self) -> Media:
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

    def build(self) -> Text:
        return Text(**self.__dict__)


class BmpBuilder(MediaBuilder):
    def __init__(self, bmp_file_name: str):
        super().__init__()
        self.bmp_file_name = bmp_file_name

    def build(self) -> Bmp:
        return Bmp(**self.__dict__)


class JpgBuilder(MediaBuilder):
    def __init__(self, jpg_file_name: str):
        super().__init__()
        self.jpg_file_name = jpg_file_name

    def build(self) -> Jpg:
        return Jpg(**self.__dict__)


class PngBuilder(MediaBuilder):
    def __init__(self, png_file_name: str):
        super().__init__()
        self.png_file_name = png_file_name

    def build(self) -> Png:
        return Png(**self.__dict__)


class GifBuilder(MediaBuilder):
    def __init__(self, gif_file_name: str):
        super().__init__()
        self.gif_file_name = gif_file_name

    def build(self) -> Gif:
        return Gif(**self.__dict__)


class MpgBuilder(MediaBuilder):
    def __init__(self, Mpg_file_name: str):
        super().__init__()
        self.mpg_file_name = Mpg_file_name

    def build(self) -> Mpg:
        return Mpg(**self.__dict__)


# ==============================================================================
# 播放项类
# ==============================================================================
class Item(BaseModel):
    media: Media
    duration: int = Field(..., ge=2, le=30000)
    screen_in: int
    play_speed: int

    def __str__(self):
        protocol = f"{self.duration},{self.screen_in},{self.play_speed},{self.media}"
        return protocol


class ItemBuilder:
    def __init__(self, media: Media):
        self.media = media
        # 单位为百分之一秒， 缺省为2
        self.duration: int = 1000
        # 缺省为0
        self.screen_in: int = ScreenInEnum.NORMAL.value
        # 播放速度
        self.play_speed: int = 0

    def build(self) -> Item:
        return Item(**self.__dict__)


# ==============================================================================
# 区域窗口类
# ==============================================================================
class Win(BaseModel):
    item_list: list[Item]
    x: int | None
    y: int | None
    w: int | None
    h: int | None

    def __str__(self):
        """格式

        第一窗口格式

        Returns:
            _type_: _description_
        """
        protocol = f"item_no={len(self.item_list)}"
        protocol += CRLF
        for i, item in enumerate(self.item_list):
            protocol += f"item{i}={item}"
            protocol += CRLF

        return protocol

    def win_str(self, win_no: int):
        """格式二

        第二窗口及以上格式按照本例

        Args:
            win_no (int): _description_

        Returns:
            _type_: _description_
        """
        protocol = f"windows{win_no}_item_no={len(self.item_list)}"
        protocol += CRLF
        for i, item in enumerate(self.item_list):
            protocol += f"windows{win_no}_item{i}={item}"
            protocol += CRLF

        return protocol


class WinBuilder:
    def __init__(self):
        self.item_list: List[Item] = []
        self.x: int | None = None
        self.y: int | None = None
        self.w: int | None = None
        self.h: int | None = None

    def build(self) -> Win:
        return Win(**self.__dict__)

    def add_item_builder(self, builder: ItemBuilder) -> "WinBuilder":
        self.item_list.append(builder.build())

        return self


# ==============================================================================
# 播放表类
# ==============================================================================
class Play(BaseModel):
    pass


class MultipleWinPlay(Play):
    """
    多窗口 playlist
    """

    win_list: list[Win]

    def __str__(self):
        protocol = "[playlist]"
        protocol += CRLF
        protocol += f"nwindows={len(self.win_list)}"
        protocol += CRLF
        for i, win in enumerate(self.win_list):
            protocol += f"windows{i}_x={win.x}"
            protocol += CRLF
            protocol += f"windows{i}_y={win.y}"
            protocol += CRLF
            protocol += f"windows{i}_w={win.w}"
            protocol += CRLF
            protocol += f"windows{i}_h={win.h}"
            protocol += CRLF
            if i == 0:
                protocol += f"{win}"
            else:
                protocol += f"{win.win_str(i)}"

        return protocol


class SingleWinPlay(Play):
    """
    单窗口 playlist
    """

    win: Win

    def __str__(self):
        protocol = "[playlist]"
        protocol += CRLF
        protocol += f"{self.win}"

        return protocol


class PlayBuilder(ABC):
    @abstractmethod
    def build(self) -> Play:
        pass


class MultipleWinPlayBuilder(PlayBuilder):
    def __init__(self):
        self.win_list: List[Win] = []

    def build(self) -> MultipleWinPlay:
        return MultipleWinPlay(**self.__dict__)

    def add_win_builder(self, builder: WinBuilder) -> "MultipleWinPlayBuilder":
        self.win_list.append(builder.build())

        return self


class SingleWinPlayBuilder(PlayBuilder):
    def __init__(self, win: Win):
        self.win = win

    def build(self) -> SingleWinPlay:
        return SingleWinPlay(**self.__dict__)
