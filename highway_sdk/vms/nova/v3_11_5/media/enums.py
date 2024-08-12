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
    """
    需要再增加
    """
    NONE = '0'
    NORMAL = '1'


class EffectSpeedEnum(str, Enum):
    SLOWEST = '0'
    SLOWER = '1'
    NORMAL = '2'
    FASTER = '3'
    FASTEST = '4'


class IsPlayTextVoiceEnum(str, Enum):
    YES = '1'
    NO = '0'


class IsSyncPlayEnum(str, Enum):
    YES = '1'
    NO = '0'


class VoiceSoundEnum(str, Enum):
    COMMON_FEMALE_VOICE = '0'
    COMMON_MALE_VOICE = '1'
    SPECIAL_MALE_VOICE = '2'
    EMOTIONAL_MALE_VOICE = '3'
    EMOTIONAL_CHILDREN_VOICE = '4'
