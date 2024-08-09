#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:FileName: textPlusMedia.py
:Project:
:Brand:
:Version:
:Description: 
:Author: He YinYu
:Link:
:Time: 2024/8/9 11:24
"""
from .baseMedia import BaseMedia
from .enums import (
    FontEnum,
    FontStyleEnum,
    ColorEnum,
    HorizontalAlignmentEnum,
    VerticalAlignmentEnum
)
from pydantic import Field, field_validator


class TextPlusMedia(BaseMedia):
    font: FontEnum
    text_size: int
    font_style: FontStyleEnum
    horizontal_alignment: HorizontalAlignmentEnum
    vertical_alignment: VerticalAlignmentEnum
    line_space: int = Field(..., ge=0, le=100)
    word_space: int = Field(..., ge=0, le=100)
    text_color: ColorEnum
    background_color: ColorEnum
    play_effect: int
    effect_speed: int
    play_count: int
    text: str
    is_play_text_voice: int
    sync_play: int
    voice_sound: int
    volume: int
    voice_speed: int
    intonation: int


    @field_validator('text_size')
    @classmethod
    def validate_text_size(cls, value: int):
        value_str = str(value)
        length = len(value_str)
        if length % 2 != 0:
            raise ValueError('Text size 格式不正确，e.g. 1616， 2424')
        elif value_str[: length / 2] != value_str[length / 2:]:
            raise ValueError('Text size 格式不正确，e.g. 1616， 2424')

    def create_msg(self):
        pass
