#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:FileName: enums.py
:Project:
:Brand:
:Version:
:Description: 
:Author: He YinYu
:Link:
:Time: 2024/8/9 10:23
"""
from enum import Enum


class FontEnum(str, Enum):
    HEI_TI = '1'
    KAI_TI = '2'
    SONG_TI = '3'
    FANG_SONG = '4'
    LI_SHU = '5'


class ColorEnum(str, Enum):
    RED = '1'
    GREEN = '2'
    BLUE = '3'
    YELLOW = '4'
    # 紫色
    PURPLE = '5'
    # 青色
    CYAN = '6'
    WHITE = '7'
    BLACK = '8'


class FontStyleEnum(str, Enum):
    NORMAL = '0'
    # 加粗
    BOLD = '1'
    # 斜体
    ITALIC = '2'
    # 下划线
    UNDERLINE = '3'
    # 中划线
    STRIKE = '4'


class AlignEnum(str, Enum):
    # 横向
    HORIZONTAL = '0'
    # 纵向
    VERTICAL = '1'


class HorizontalAlignmentEnum(str, Enum):
    LEFT = '0'
    RIGHT = '1'
    CENTER = '2'


class VerticalAlignmentEnum(str, Enum):
    TOP = '0'
    BOTTOM = '1'
    CENTER = '2'


class PlayEffectEnum(str, Enum):
    NONE = '0'
