from abc import abstractmethod
from enum import IntEnum, StrEnum
from ftplib import CRLF
from typing import Literal, Self

from pydantic import BaseModel, Field

from highway_sdk.vendors.vms._base import BaseBuilder

# TODO: 修改


# ==============================================================================
# 枚举类
# ==============================================================================
class ScreenInMode(IntEnum):
    NORMAL = 1


class Color(StrEnum):
    RED = "255000000000"
    GREEN = "000255000000"
    YELLOW = "255255000000"
    BLACK = "000000000000"


class Font(StrEnum):
    HEI_TI = "h"
    KAI_TI = "k"
    SONG_TI = "s"
    FANG_SONG = "f"


class FontSize(IntEnum):
    SIZE_16 = 16
    SIZE_24 = 24
    SIZE_32 = 32
    SIZE_48 = 48
    SIZE_64 = 64


class Esc(StrEnum):
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
class BaseMedia(BaseModel):
    x: int = Field(..., ge=0, le=999)
    y: int = Field(..., ge=0, le=999)


class Text(BaseMedia):
    font_color: Color | None
    background_color: Color | None
    word_space: int | None = Field(None, ge=0, le=99)
    font: Font | None
    font_size: FontSize | None
    text: str

    def __str__(self):
        # TODO: 增加灵活性，根据赋值的顺序，决定输出字符串的顺序
        protocol = f"{Esc.XY.value}{self.x:03d}{self.y:03d}"
        if self.font:
            protocol += f"{Esc.FONT.value}{self.font.value}"
        if self.font_size:
            protocol += f"{self.font_size.value}{self.font_size.value}"
        if self.font_color:
            protocol += f"{Esc.FONT_COLOR.value}{self.font_color.value}"
        if self.background_color:
            protocol += f"{Esc.BACKGROUND_COLOR.value}{self.background_color.value}"
        if self.word_space:
            protocol += f"{Esc.WORD_SPACE.value}{self.word_space:02d}"
        protocol += f"{self.text}"

        return protocol


class Bmp(BaseMedia):
    bmp_file_name: str

    def __str__(self):
        protocol = f"{Esc.XY.value}{self.x:03d}{self.y:03d}{Esc.BMP.value}{self.bmp_file_name}"
        return protocol


class Png(BaseMedia):
    png_file_name: str

    def __str__(self):
        protocol = f"{Esc.XY.value}{self.x:03d}{self.y:03d}{Esc.PNG.value}{self.png_file_name}"
        return protocol


class Jpg(BaseMedia):
    jpg_file_name: str

    def __str__(self):
        protocol = f"{Esc.XY.value}{self.x:03d}{self.y:03d}{Esc.JPG.value}{self.jpg_file_name}"
        return protocol


class Gif(BaseMedia):
    gif_file_name: str

    def __str__(self):
        protocol = f"{Esc.XY.value}{self.x:03d}{self.y:03d}{Esc.GIF.value}{self.gif_file_name}"
        return protocol


class Mpg(BaseMedia):
    """
    video
    """

    mpg_file_name: str

    def __str__(self):
        protocol = f"{Esc.XY.value}{self.x:03d}{self.y:03d}{Esc.MPG.value}{self.mpg_file_name}"
        return protocol


# ==============================================================================
# 媒体构造类
# ==============================================================================
class MediaBuilder(BaseBuilder):
    def __init__(self):
        self.x: int = 0
        self.y: int = 0


class TextBuilder(MediaBuilder):
    def __init__(self, text: str):
        super().__init__()

        # 文本
        self.text = text
        self.font_color: Color | None = None
        self.background_color: Color | None = None
        # 字间距
        self.word_space: int = 0
        # 输入示例 h
        self.font: Font | None = None
        # 输入示例 16
        self.font_size: FontSize | None = None

    def build(self) -> Text:
        return Text(**self.__dict__)

    def set_font_color(self, color: Literal["red", "green", "yellow", "black"]):
        self.font_color = Color[color.upper()]

    def set_background_color(self, color: Literal["red", "green", "yellow", "black"]):
        self.background_color = Color[color.upper()]

    def set_font(self, font: Literal["hei_ti", "kai_ti", "song_ti", "fang_song"]):
        self.font = Font[font.upper()]

    def set_font_size(self, font_size: Literal[16, 24, 32, 48, 64]):
        self.font_size = FontSize[f"SIZE_{font_size}"]

    def set_word_space(self, word_space: int):
        self.word_space = word_space

    def set_xy(self, x: int, y: int):
        self.x = x
        self.y = y


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
    def __init__(self, mpg_file_name: str):
        super().__init__()
        self.mpg_file_name = mpg_file_name

    def build(self) -> Mpg:
        return Mpg(**self.__dict__)


# ==============================================================================
# 播放项类
# ==============================================================================


class Item(BaseModel):
    media_list: list[BaseMedia]
    duration: int = Field(..., ge=2, le=30000)
    screen_in: int
    play_speed: int

    def __str__(self):
        media_str = "".join(str(media) for media in self.media_list)
        protocol = f"{self.duration},{self.screen_in},{self.play_speed},{media_str}"

        return protocol


class ItemBuilder(BaseBuilder):
    def __init__(
        self,
        duration: int = 1000,
        screen_in: int = ScreenInMode.NORMAL,
        play_speed: int = 0,
    ):
        self.media_list: list[BaseMedia] = []
        self.duration = duration  # 单位为百分之一秒， 缺省为2
        self.screen_in = screen_in  # 缺省为0
        self.play_speed = play_speed  # 播放速度

    def build(self) -> Item:
        if len(self.media_list) == 0:
            raise ValueError("No media")
        return Item(**self.__dict__)

    def add_text_media(
        self,
        text: str,
        *,
        font: Literal["hei_ti", "kai_ti", "song_ti", "fang_song"] = "hei_ti",
        font_size: Literal[16, 24, 32, 48, 64] = 16,
        font_color: Literal["red", "yellow", "green", "black"] = "yellow",
        x: int = 0,
        y: int = 0,
        background_color: Literal["red", "yellow", "green", "black"] = "black",
        word_space: int = 0,
    ):
        builder = TextBuilder(text)
        builder.set_xy(x, y)
        builder.set_font_color(font_color)
        builder.set_background_color(background_color)
        builder.set_word_space(word_space)
        builder.set_font(font)
        builder.set_font_size(font_size)
        self._add_media_builder(builder)

    def add_image_media(
        self,
        media_type: Literal["bmp", "gif", "jpg", "png", "mpg"],
        *,
        file_name: str,
        x: int = 0,
        y: int = 0,
    ):
        builders = {
            "bmp": BmpBuilder,
            "gif": GifBuilder,
            "jpg": JpgBuilder,
            "png": PngBuilder,
            "mpg": MpgBuilder,
        }
        builder_name = media_type.lower()
        if builder_name not in builders:
            raise ValueError(f"Unsupported media type: {media_type}")

        builder = builders[builder_name](file_name)
        builder.x = x
        builder.y = y
        self._add_media_builder(builder)

    def _add_media_builder(self, media_builder: MediaBuilder) -> Self:
        """添加媒体建造器

        允许有且只有一个text媒体类型，且位于媒体列表最后面

        Args:
            media_builder (MediaBuilder): _description_

        Raises:
            ValueError: _description_

        Returns:
            Self: _description_
        """
        media = media_builder.build()
        if isinstance(media, Text):
            for existing_media in self.media_list:
                if isinstance(existing_media, Text):
                    raise ValueError("Only one text media is allowed per item.")
            self.media_list.append(media)
        else:
            insert_index = len(self.media_list)
            for i, existing_media in enumerate(self.media_list):
                if isinstance(existing_media, Text):
                    insert_index = i
                    break
            self.media_list.insert(insert_index, media)
        return self


# ==============================================================================
# 窗口类
# ==============================================================================
class Window(BaseModel):
    item_list: list[Item]
    x: int
    y: int
    w: int
    h: int

    def __str__(self):
        """格式

        第一窗口格式

        Returns:
            _type_: _description_
        """
        protocol = f"item_no={len(self.item_list)}"
        protocol += CRLF
        for i, item_builder in enumerate(self.item_list):
            protocol += f"item{i}={item_builder}"
            protocol += CRLF

        return protocol

    def _win_str(self, win_no: int):
        """格式二

        第二窗口及以上格式按照本例

        Args:
            win_no (int): _description_

        Returns:
            _type_: _description_
        """
        if win_no < 1:
            raise ValueError("win_no must be greater than 0")

        protocol = f"windows{win_no}_item_no={len(self.item_list)}"
        protocol += CRLF
        for i, item in enumerate(self.item_list):
            protocol += f"windows{win_no}_item{i}={item}"
            protocol += CRLF

        return protocol


class WindowBuilder(BaseBuilder):
    def __init__(self, x: int = 0, y: int = 0, w: int = 32, h: int = 32):
        self.item_list: list[Item] = []
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self._item_builder_list: list[ItemBuilder] = []

    def build(self) -> Window:
        self.item_list = [item.build() for item in self._item_builder_list]
        return Window(**self.__dict__)

    def new_item(
        self,
        duration: int = 1000,
        screen_in: int = ScreenInMode.NORMAL,
        play_speed: int = 0,
    ) -> ItemBuilder:
        try:
            ib = ItemBuilder(duration, screen_in, play_speed)
            return ib
        finally:
            self._item_builder_list.append(ib)


# ==============================================================================
# 播放表类
# ==============================================================================
class Play(BaseModel):
    pass


class MultipleWinPlay(Play):
    """
    多窗口 playlist
    """

    windows: list[Window]

    def __str__(self):
        protocol = "[playlist]"
        protocol += CRLF
        protocol += f"nwindows={len(self.windows)}"
        protocol += CRLF
        for i, window in enumerate(self.windows):
            protocol += f"windows{i}_x={window.x}"
            protocol += CRLF
            protocol += f"windows{i}_y={window.y}"
            protocol += CRLF
            protocol += f"windows{i}_w={window.w}"
            protocol += CRLF
            protocol += f"windows{i}_h={window.h}"
            protocol += CRLF
            if i == 0:
                protocol += f"{window}"
            else:
                protocol += f"{window._win_str(i)}"

        return protocol


class SingleWinPlay(Play):
    """
    单窗口 playlist
    """

    window: Window

    def __str__(self):
        protocol = "[playlist]"
        protocol += CRLF
        protocol += f"{self.window}"

        return protocol


class BasePlayBuilder(BaseBuilder):
    mode: str

    @abstractmethod
    def new_window(self, *args, **kwargs) -> WindowBuilder:
        pass


class PlayFactory:
    """play构造工厂类


    Examples:
        1. single 模式

    >>> pf = PlayFactory("single")
    >>> with pf.get_play_builder() as pb:
    >>>     with pb.new_window() as wb:
    >>>         with wb.new_item() as ib:
    >>>             ib.add_image_media("bmp", file_name="001")
    >>>             ib.add_text_media("文本测试")
    >>>         with wb.new_item() as ib:
    >>>             ib.add_image_media("jpg", file_name="002")
    >>> print(pf.get_play())

        2. multiple 模式

    >>> pf = PlayFactory("single")
    >>> with pf.get_play_builder() as pb:
    >>>     with pb.new_window() as wb:
    >>>         with wb.new_item() as ib:
    >>>             ib.add_image_media("bmp", file_name="001")
    >>>             ib.add_text_media("文本测试")
    >>>         with wb.new_item() as ib:
    >>>             ib.add_image_media("jpg", file_name="002")
    >>>     with pb.new_window() as wb:
    >>>         with wb.new_item() as ib:
    >>>             ib.add_image_media("bmp", file_name="001")
    >>>             ib.add_text_media("文本测试")
    >>>         with wb.new_item() as ib:
    >>>             ib.add_image_media("jpg", file_name="002")
    >>> print(pf.get_play())
    """

    _play_builders: dict[str, type[BasePlayBuilder]] = {}  # noqa: RUF012

    def __init__(self, mode: Literal["single", "multiple"]) -> None:
        if mode not in self._play_builders:
            raise ValueError(f"Unsupported mode: {mode}. Available modes: {list(self._play_builders.keys())}")
        self._mode = mode
        self._play_builder: BasePlayBuilder | None = None

    @classmethod
    def register(cls, builder_class: type[BasePlayBuilder]):
        if not issubclass(builder_class, BasePlayBuilder):
            raise TypeError(f"{builder_class} must inherit from BasePlayBuilder")
        cls._play_builders[builder_class.mode] = builder_class
        return builder_class

    def get_play_builder(self):
        if self._play_builder is None:
            self._play_builder = self._play_builders[self._mode]()
        return self._play_builder

    def get_play(self):
        if self._play_builder is None:
            raise ValueError("Play Builder is None")
        return self._play_builder.build()


@PlayFactory.register
class MultipleWindowPlayBuilder(BasePlayBuilder):
    mode = "multiple"

    def __init__(self):
        self.window_list: list[Window] = []
        self._window_builder_list: list[WindowBuilder] = []

    def build(self) -> MultipleWinPlay:
        self.window_list = [builder.build() for builder in self._window_builder_list]
        return MultipleWinPlay(**self.__dict__)

    def new_window(
        self,
        x: int = 0,
        y: int = 0,
        w: int = 32,
        h: int = 32,
    ) -> WindowBuilder:
        try:
            wb = WindowBuilder(x, y, w, h)
            return wb
        finally:
            self._window_builder_list.append(wb)


@PlayFactory.register
class SingleWindowPlayBuilder(BasePlayBuilder):
    mode = "single"

    def __init__(self):
        self.window = None
        self._window_builder: WindowBuilder | None = None

    def build(self) -> SingleWinPlay:
        if self._window_builder is None:
            raise ValueError("window_builder is None")
        self.window = self._window_builder.build()
        return SingleWinPlay(**self.__dict__)

    def new_window(
        self,
        x: int = 0,
        y: int = 0,
        w: int = 32,
        h: int = 32,
    ) -> WindowBuilder:
        try:
            wb = WindowBuilder(x, y, w, h)
            return wb
        finally:
            self._window_builder = wb


__all__ = ["PlayFactory"]
