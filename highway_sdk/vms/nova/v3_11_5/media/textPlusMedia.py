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
    VerticalAlignmentEnum,
    PlayEffectEnum,
    EffectSpeedEnum,
    IsPlayTextVoiceEnum,
    IsSyncPlayEnum,
    VoiceSoundEnum,
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
    play_effect: PlayEffectEnum
    effect_speed: EffectSpeedEnum
    play_count: int = Field(..., ge=0, le=255)
    text: str
    is_play_text_voice: IsPlayTextVoiceEnum
    is_sync_play: IsSyncPlayEnum
    voice_sound: VoiceSoundEnum
    volume: int = Field(..., ge=0, le=9)
    voice_speed: int = Field(..., ge=0, le=9)
    intonation: int = Field(..., ge=0, le=9)

    @field_validator('text_size')
    @classmethod
    def validate_text_size(cls, value: int):
        value_str = str(value)
        length = len(value_str)
        half_len = int(length / 2)
        if length % 2 != 0:
            raise ValueError('Text size 格式不正确，e.g. 1616， 2424')
        elif value_str[:half_len] != value_str[half_len:]:
            raise ValueError('Text size 格式不正确，e.g. 1616， 2424')
        else:
            return value
    def create_msg(self):
        protocol = (f'txtext{self.index}='
                    f'{self.x},'
                    f'{self.y},'
                    f'{self.width},'
                    f'{self.height},'
                    f'{self.font},'
                    f'{self.text_size},'
                    f'{self.font_style},'
                    f'{self.horizontal_alignment},'
                    f'{self.vertical_alignment},'
                    f'{self.line_space},'
                    f'{self.word_space},'
                    f'{self.text_color},'
                    f'{self.background_color},'
                    f'{self.play_effect},'
                    f'{self.effect_speed},'
                    f'{self.duration},'
                    f'{self.play_count},'
                    f'{self.text},'
                    f'{self.is_play_text_voice},'
                    f'{self.is_sync_play},'
                    f'{self.voice_sound},'
                    f'{self.volume},'
                    f'{self.voice_speed},'
                    f'{self.intonation}')

        return protocol
