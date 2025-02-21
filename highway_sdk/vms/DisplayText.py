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
        >>> dtb = DisplayTextBuilder(text='一二三四五六七八九十', h=96, w=96, max_size=275, min_size=6)
        >>> dtb.build_image().show()
        >>> print(dtb.dt.size)
        24
        >>> print(dtb.dt.text)
        一二三四
        五六七八
        九十
        >>> print(dtb.dt.xy)
        (0, 10)
        >>> print(dtb.dt.line_list)
        ['一二三四', '五六七八', '九十']
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
        # 合理的最大字号最大不超过h和w的最小值
        self.max_size = min(max_size, min(h, w))
        # 合理的最小字号最小不小过8
        self.min_size = max(min_size, 8)
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
        def calc_text_dimensions(size):
            total_width = 0
            total_height = 0
            max_lines = 1  # 默认至少一行
            clw = 0  # 当前行宽度

            letter_s = self.dt.letter_spacing
            line_s = self.dt.line_spacing
            text = self.text
            width = self.w
            height = self.h

            for i, ch in enumerate(text):
                ch_w = size / 2 if self.is_ascall(ch) else size

                if ch_w == 0:
                    ch_w += ch_w
                else:
                    clw += letter_s + ch_w

                # 判断是否需要换行
                if (clw + letter_s > width) or (clw + letter_s + size > width):

                    max_lines += 1

                    # 换行后计算总高度
                    total_height = max_lines * size + (max_lines - 1) * line_s

                    if total_height > height:
                        return total_width, total_height

                    total_width = max(clw, total_width)
                    clw = 0

            return total_width, total_height

        left, right = self.min_size, self.max_size
        best_size = self.min_size

        while left <= right:
            mid = (left + right) // 2

            text_width, text_height = calc_text_dimensions(mid)

            if text_width <= self.w and text_height <= self.h:
                best_size = mid
                left = mid + 1
            else:
                right = mid - 1

        self.dt.size = best_size

    def _build_line_list(self) -> None:
        """
        获取换行调整的文本

        :return:
        """
        clw = 0  # 当前行宽
        letter_s = self.dt.letter_spacing
        ch_list = []
        for i, ch in enumerate(self.text):
            ch_list.append(ch)

            ch_w = self.dt.size / 2 if self.is_ascall(ch) else self.dt.size
            if clw == 0:
                clw += ch_w
            else:
                clw += letter_s + ch_w

            # 排除最后一个字符
            if i != (len(self.text) - 1):
                if (clw + letter_s > self.w) or (clw + letter_s + ch_w > self.w):
                    ch_list.append(self.dt.lf)
                    clw = 0

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
        生成预览图像

        :return:
        :rtype: Image
        """
        if self.dt.size is None:
            self._build_adjusted_size()
        if self.dt.line_list is None:
            self._build_line_list()
        if self.dt.xy is None:
            self._build_xy()

        img = Image.new('RGB', (self.w, self.h), self.bg_color)
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype("simhei.ttf", self.dt.size)
        draw.text(self.dt.xy, self.dt.text, fill=self.dt.color, font=font)

        return img


