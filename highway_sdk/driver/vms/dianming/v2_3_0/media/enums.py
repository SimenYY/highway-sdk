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
:Time: 2024/8/20 16:16
"""
from enum import Enum


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
    SIZE_72 = 7272
    SIZE_80 = 8080
    SIZE_88 = 8888
    SIZE_96 = 9696
    SIZE_104 = 104104
    SIZE_112 = 112112
    SIZE_120 = 120120

