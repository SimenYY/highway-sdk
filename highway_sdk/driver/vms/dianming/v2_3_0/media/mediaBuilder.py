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
:Time: 2024/8/20 13:53
"""
from .media import Media
from .baseBuilder import BaseBuilder


class MediaBuilder(BaseBuilder):
    def __init__(self):
        # 增加使用性，增加的属性
        self._x: int = 0
        self._y: int = 0
        # bmp 图片文件
        self._bmp_file_name: str = ''
        # png 图片文件
        self._png_file_name: str = ''
        # jpg 图片文件
        self._jpg_file_name: str = ''
        # gif 图片文件
        self._gif_file_name: str = ''
        self._text_color: str = '255255000000'  # yellow
        self._background_color: str = '000000000000'  # black
        # 字间距
        self._word_space: int = 0
        # 输入示例 h
        self._font: str = 'h'
        # 输入示例 16
        self._text_size: int = 1616

        self._text: str = ''

    def build(self) -> Media:
        return Media(**self.to_dict())

    @property
    def x(self) -> int:
        return self._x

    @x.setter
    def x(self, x: int) -> None:
        self._x = x

    @property
    def y(self) -> int:
        return self._y

    @y.setter
    def y(self, y: int) -> None:
        self._y = y

    @property
    def bmp_file_name(self) -> str:
        return self._bmp_file_name

    @bmp_file_name.setter
    def bmp_file_name(self, bmp_file_name: str) -> None:
        self._bmp_file_name = bmp_file_name

    @property
    def png_file_name(self) -> str:
        return self._png_file_name

    @png_file_name.setter
    def png_file_name(self, png_file_name: str) -> None:
        self._png_file_name = png_file_name

    @property
    def jpg_file_name(self) -> str:
        return self._jpg_file_name

    @jpg_file_name.setter
    def jpg_file_name(self, jpg_file_name: str) -> None:
        self._jpg_file_name = jpg_file_name

    @property
    def gif_file_name(self) -> str:
        return self._gif_file_name

    @gif_file_name.setter
    def gif_file_name(self, gif_file_name: str) -> None:
        self._gif_file_name = gif_file_name

    @property
    def text_color(self) -> str:
        return self._text_color

    @text_color.setter
    def text_color(self, text_color: str) -> None:
        self._text_color = text_color

    @property
    def background_color(self) -> str:
        return self._background_color

    @background_color.setter
    def background_color(self, background_color: str) -> None:
        self._background_color = background_color

    @property
    def word_space(self) -> int:
        return self._word_space

    @word_space.setter
    def word_space(self, word_space: int) -> None:
        self._word_space = word_space

    @property
    def font(self) -> str:
        return self._font

    @font.setter
    def font(self, font: str) -> None:
        self._font = font

    @property
    def text_size(self) -> int:
        return self._text_size

    @text_size.setter
    def text_size(self, text_size: int) -> None:
        size_str = str(text_size)
        self._text_size = int(f'{size_str}{size_str}')

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, text: str) -> None:
        self._text = text
