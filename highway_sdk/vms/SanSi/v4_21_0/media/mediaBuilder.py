#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:FileName: mediaBuilder.py
:Project:
:Brand:
:Version:
:Description: 
:Author: He YinYu
:Link:
:Time: 2025/4/17 10:22
"""
from abc import abstractmethod, ABC

from .enums import ColorEnum, FontEnum, TextSizeEnum
from .media import Media, Text, Bmp, Jpg, Gif, Mpg, Png

__all__ = [
    "TextBuilder",
    "BmpBuilder",
    "GifBuilder",
    "MpgBuilder",
    "PngBuilder",
    "JpgBuilder",
]


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
