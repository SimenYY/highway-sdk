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

    def create_msg(self):
        protocol = (f'txtext{self.index}='
                    f'{self.x},'
                    f'{self.y},'
                    f'{self.width},'
                    f'{self.height},'
                    f'{self.font},'
                    f'{self.text_size}{self.text_size},'
                    f'{self.font_style.value},'
                    f'{self.horizontal_alignment.value},'
                    f'{self.vertical_alignment.value},'
                    f'{self.line_space},'
                    f'{self.word_space},'
                    f'{self.text_color.value},'
                    f'{self.background_color.value},'
                    f'{self.play_effect.value},'
                    f'{self.effect_speed.value},'
                    f'{self.duration},'
                    f'{self.play_count},'
                    f'{self.text},'
                    f'{self.is_play_text_voice.value},'
                    f'{self.is_sync_play.value},'
                    f'{self.voice_sound.value},'
                    f'{self.volume},'
                    f'{self.voice_speed},'
                    f'{self.intonation}')

        return protocol
