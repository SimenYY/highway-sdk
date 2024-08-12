#!/usr/bin/env python
# -- coding: utf-8 --

from .baseMedia import BaseMedia
from .baseMediaBuilder import BaseMediaBuilder
from .textMedia import TextMedia
from .enums import (
    FontEnum,
    FontStyleEnum,
    ColorEnum,
    AlignEnum
)


class TextMediaBuilder(BaseMediaBuilder):

    def __init__(self):
        super().__init__()

        # 字体
        self._font: str = FontEnum.HEI_TI.value
        # 字体大小
        self._text_size: int = 1616
        # 字体颜色
        self._text_color: str = ColorEnum.RED.value
        # 背景颜色
        self._background_color: str = ColorEnum.BLACK.value
        # 文本内容
        self._text: str = ''
        # 闪烁
        self._flash: str = '0'
        # 字体风格
        self._font_style: int = FontStyleEnum.NORMAL.value
        # 字符间距
        self._world_space: int = 0
        # 字符排列方向
        self._alignment_direction: int = AlignEnum.HORIZONTAL.value

    def build(self) -> BaseMedia:
        return TextMedia(**self.to_dict())

    @property
    def font(self) -> str:
        return self._font

    @font.setter
    def font(self, font: str) -> None:
        """
        1-黑体
        2-楷体
        3-宋体
        4-仿宋
        5-隶书
        可以使用字体名称，如 arial 等。

        :param font:
        :return:
        """
        self._font = font

    @property
    def text_size(self) -> int:
        return self._text_size

    @text_size.setter
    def text_size(self, text_size: int) -> None:
        """
        字体大小，单位像素。由宽度和高度组成，宽高各占两个字符。如 0808、3232，
        999999，对应的字体大小是 8、32、999。

        :param text_size:
        :return:
        """
        size_str = str(text_size)
        self._text_size = int(f'{size_str}{size_str}')

    @property
    def text_color(self) -> str:
        return self._text_color

    @text_color.setter
    def text_color(self, text_color: str) -> None:
        """
        1-红色
        2-绿色
        3-蓝色
        4-黄色
        5-紫色
        6-青色
        7-白色
        8-黑色
        可以使用 RGB 定义，
        如 FF0000 表示红色

        :param text_color:
        :return:
        """
        self._text_color = text_color

    @property
    def background_color(self) -> str:
        return self._background_color

    @background_color.setter
    def background_color(self, background_color: str) -> None:
        """
        同text_color

        :param background_color:
        :return:
        """
        self._background_color = background_color

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, text: str) -> None:
        self._text = text

    @property
    def flash(self) -> str:
        return self._flash

    @flash.setter
    def flash(self, flash: str) -> None:
        self._flash = flash

    @property
    def font_style(self) -> int:
        return self._font_style

    @font_style.setter
    def font_style(self, font_style: int) -> None:
        """
        0-常规
        1-加粗
        2-倾斜
        4-下划线
        8-中划线字体风格可以组合，
        例如 3 表示加粗且倾斜显示

        :param font_style:
        :return:
        """
        self._font_style = font_style

    @property
    def world_space(self) -> int:
        return self._world_space

    @world_space.setter
    def world_space(self, world_space: int) -> None:
        """
        字符间隔大小，单位像素 0-1000

        :param world_space:
        :return:
        """
        self._world_space = world_space

    @property
    def alignment_direction(self) -> int:
        return self._alignment_direction

    @alignment_direction.setter
    def alignment_direction(self, alignment_direction: int) -> None:
        """
        横向排列 0
        纵向排列 1
        :param alignment_direction:
        :return:
        """

        self._alignment_direction = alignment_direction
