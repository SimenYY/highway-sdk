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
:Time: 2025/4/17 10:13
"""
from enum import Enum


class ScreenInEnum(int, Enum):
    NORMAL = 1


class ColorEnum(str, Enum):
    RED = '255000000000'
    GREEN = '000255000000'
    YELLOW = '255255000000'
    BLACK = '000000000000'


class FontEnum(str, Enum):
    HEI_TI = 'h'
    KAI_TI = 'k'
    SONG_TI = 's'
    FANG_SONG = 'f'


class TextSizeEnum(int, Enum):
    SIZE_16 = 1616
    SIZE_24 = 2424
    SIZE_32 = 3232
    SIZE_48 = 4848
    SIZE_64 = 6464
