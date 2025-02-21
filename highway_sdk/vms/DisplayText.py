#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:FileName: utils.py
:Project:
:Brand:
:Version:
:Description: 
:Author: He YinYu
:Link:
:Time: 2025/2/20 11:24
"""
import math
from typing import List, Tuple

from pydantic import BaseModel

from PIL import Image, ImageDraw, ImageFont


class DisplayText(BaseModel):
    """
    显示文本类，在原生文字的基础上，做了自适应换行
    """
    # 所用换行符
    lf: str = None
    # 字间距
    letter_spacing: int = None
    # 行间距
    line_spacing: int = None
    # 显示文本, 已经处理过的
    text: str = None
    # 显示文本颜色
    color: str = None
    # 字体大小，已经处理过的
    size: int = None
    # 显示文本按行列表
    line_list: List[str] = None
    # 起始坐标，左上角
    xy: Tuple[int, int] = None


class DisplayTextBuilder:
    """
    构造显示字符串

    Usage::
    >>>dtb = DisplayTextBuilder(text='一二三四五六七八九十', h=96, w=96, max_size=96, min_size=8)
    >>>dt = dtb.build()
    >>>print(dt.text)
    一二三四
    五六七八
    九十
    >>>print(dt.xy)
    (0, 10)
    >>>print(dt.size)
    24
    >>>dtb.build_image()
    >>>image = dtb.build_image()
    >>>image.show()
    """

    def __init__(
            self,
            text: str,
            *,
            h: int,
            w: int,
            max_size: int,
            min_size: int,
            text_color: str = 'red',
            bg_color: str = 'black',
            line_spacing: int = 1,
            letter_spacing: int = 0,
            size_list: list = None,
            lf: str = '\n'

    ):
        self.text = text
        self.h = h
        self.w = w
        self.max_size = max_size
        self.min_size = min_size
        self.bg_color = bg_color
        # 如果设备仅支持部分字库，则传入支持的字库列表
        if size_list is None:
            self.size_list = []
        self.lf = lf

        self.dt: DisplayText = DisplayText()
        self.dt.lf = self.lf
        self.dt.line_spacing = line_spacing
        self.dt.letter_spacing = letter_spacing
        self.dt.color = text_color

    @staticmethod
    def is_ascall(ch) -> bool:
        """
        判断是否为ascall字符

        :param ch:
        :return:
        :rtype: bool
        """
        return 0 <= ord(ch) <= 127

    def _calc_text_len(self, size: int, text: str) -> int:
        """
        计算文本占阵列大小总长度

        :param size: 字体大小
        :return:
        :rtype: int
        """
        length = 0
        for ch in text:
            if self.is_ascall(ch):
                length += size / 2 + self.dt.letter_spacing
            else:
                length += size + self.dt.letter_spacing
        return length - self.dt.letter_spacing

    @staticmethod
    def max_less_than(compared: int, size_list: List[int]) -> int | None:
        """
        该函数用于在给定的整数列表size_list中找出小于或等于compared的最大值

        :param compared:
        :param size_list:
        :return:
        :rtype: int or None
        """
        return max((size for size in size_list if size <= compared), default=None)

    def build(self) -> DisplayText:
        """
        返回显示文本

        :return:
        """
        self._build_adjusted_size()
        self._build_line_list()
        self._build_xy()

        return self.dt

    def _build_adjusted_size(self) -> None:
        """
        获取合适的字体

        :return:
        """
        size = self.max_size
        rows = 1
        while size > self.min_size:
            # 计算当前行数的最小字号，例如只有一行字，那字号的范围便是h ~ h/2
            curr_rows_min_size = (self.h - (rows * self.dt.line_spacing)) / (rows + 1)
            # 在当前行数时，判断最合适字号是否在该字号范围内
            while size >= curr_rows_min_size:
                # 计算当前字号时，下发字符总长度
                length = self._calc_text_len(size=size, text=self.text)
                # 如果一行显示长度超过了显示区域宽度，则减少字号，否则就是找到
                if length / rows > self.w:
                    size -= 1
                else:
                    # 判断是否超出显示高度
                    if math.ceil(len(self.text) / math.floor(self.w / size)) * size > self.h:
                        size -= 1
                    else:
                        break
            if size >= curr_rows_min_size:
                break
            else:
                rows += 1

        target_size = self.max_less_than(size, self.size_list)

        if target_size is None:
            target_size = size

        self.dt.size = target_size

    def _build_line_list(self) -> None:
        """
        获取换行调整的文本

        :return:
        """
        length = 0
        ch_list = list(self.text)
        for i, ch in enumerate(self.text):
            if self.is_ascall(ch):
                length += self.dt.size / 2 + self.dt.letter_spacing
            else:
                length += self.dt.size + self.dt.letter_spacing

            if length > self.w:
                ch_list.insert(i, self.lf)
                length = 0

        self.dt.text = ''.join(ch_list)
        self.dt.line_list = self.dt.text.split(self.lf)

    def _build_xy(self) -> None:
        """
        输出文本显示坐标点，默认左上角

        :return:
        """
        first_line = self.dt.line_list[0]
        first_line_len = self._calc_text_len(self.dt.size, first_line)
        x = (self.w - first_line_len) / 2

        rows = len(self.dt.line_list)
        y = (self.h - rows * (self.dt.size + self.dt.line_spacing) - self.dt.line_spacing) / 2

        self.dt.xy = (round(x), round(y))

    def build_image(self) -> Image:
        """
        生成预览接口

        :return:
        """
        if self.dt.size is None:
            self._build_adjusted_size()
        if self.dt.line_list is None:
            self._build_line_list()
        if self.dt.xy is None:
            self._build_xy()

        img = Image.new('RGB', (self.h, self.w), self.bg_color)
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype("simhei.ttf", self.dt.size)
        draw.text(self.dt.xy, self.dt.text, fill=self.dt.color, font=font)

        return img

