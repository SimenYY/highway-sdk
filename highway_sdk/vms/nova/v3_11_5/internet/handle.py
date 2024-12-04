#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:FileName: handle.py
:Project:
:Brand:
:Version:
:Description: 
:Author: He YinYu
:Link:
:Time: 2024/12/3 17:22
"""
from typing import List
import math


class TextHandler:

    def __init__(
            self,
            text: str,
            h: int,
            w: int,
            max_font_size: int = None,
            min_font_size: int = None,
            line_spacing: int = 1,
            letter_spacing: int = 0,
            font_size_list: list = None
    ):
        # 对英文逗号进行转义
        self.text = text.replace(',', '\,')
        # 显示区域高度
        self.h = h
        # 显示区域宽度
        self.w = w

        if max_font_size is None:
            self.max_font_size = min(h, w)
        else:
            self.max_font_size = max_font_size

        if min_font_size is None:
            self.min_font_size = 8
        else:
            self.min_font_size = min_font_size
        # 行间距
        self.line_spacing = line_spacing
        # 字间距
        self.letter_spacing = letter_spacing
        # 如果提供了情报板支持的字库列表，则最终从列表中选择合适的字号。
        self.font_size_list = font_size_list

    @classmethod
    def is_ascall(cls, ch):
        return 0 <= ord(ch) <= 127

    @classmethod
    def calc_text_len(cls, text: str, size: int, letter_spacing=0):
        """
        计算文本占阵列大小总长度

        :param text:
        :param size:
        :param letter_spacing:
        :return:
        """
        ch_list = list(text)
        length = 0
        for ch in ch_list:
            if cls.is_ascall(ch):
                length += size / 2 + letter_spacing
            else:
                length += size + letter_spacing
        return length

    @staticmethod
    def max_less_than(compared: int, size_list: List[int]) -> int | None:
        if size_list is None:
            return None
        return max((size for size in size_list if size <= compared), default=None)

    def text_wrap(self, text: str, size: int, width: int, letter_spacing: int = 0) -> str:
        """
        文本换行

        :param text:
        :param size:
        :param width:
        :param letter_spacing:
        :return:
        """
        length = 0
        ch_list = list(text)
        for i, ch in enumerate(ch_list):
            if self.is_ascall(ch):
                length += size / 2 + letter_spacing
            else:
                length += size + letter_spacing

            if length > width:
                ch_list.insert(i, '\n')
                length = 0

        return ''.join(ch_list)

    def adjust_text(self) -> str:
        """
        调整文本

        :return:
        """
        size = self.max_font_size
        rows = 1
        while size > self.min_font_size:
            # 计算当前行数的最小字号，例如只有一行字，那字号的范围便是h ~ h/2
            curr_rows_min_size = (self.h - (rows * self.line_spacing)) / (rows + 1)
            # 在当前行数时，判断最合适字号是否在该字号范围内
            while size >= curr_rows_min_size:
                # 计算当前字号时，下发字符总长度
                length = self.calc_text_len(text=self.text, size=size, letter_spacing=self.letter_spacing)
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

        target = self.max_less_than(size, self.font_size_list)

        if target is None:
            target = size
        print(size)
        return self.text_wrap(self.text, target, self.w, self.letter_spacing)


if __name__ == '__main__':
    th = TextHandler(text='喝酒不开车，开车不喝酒', h=60, w=600)
    print(th.adjust_text())
