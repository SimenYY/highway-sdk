#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:FileName: textPlusMediaBuilder.py
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
from .baseMediaBuilder import BaseMediaBuilder
from .textPlusMedia import TextPlusMedia


class TextPlusMediaBuilder(BaseMediaBuilder):

    def __init__(self):
        super().__init__()

        self._font: str = FontEnum.HEI_TI.value
        self._text_size: int = 1616
        self._font_style: str = FontStyleEnum.NORMAL.value
        self._horizontal_alignment: str = HorizontalAlignmentEnum.LEFT.value
        self._vertical_alignment: str = VerticalAlignmentEnum.TOP.value
        self._line_space: int = 1
        self._word_space: int = 0
        self._text_color: str = ColorEnum.RED.value
        self._background_color: str = ColorEnum.BLACK.value
        self._play_effect: str = PlayEffectEnum.NONE.value
        self._effect_speed: str = EffectSpeedEnum.NORMAL.value
        self._play_count: int = 1
        self._text: str = ''
        self._is_play_text_voice: str = IsPlayTextVoiceEnum.NO.value
        self._is_sync_play: str = IsSyncPlayEnum.NO.value
        self._voice_sound: str = VoiceSoundEnum.COMMON_FEMALE_VOICE.value
        self._volume: int = 5
        self._voice_speed: int = 5
        self._intonation: int = 5

    def auto_adjust_text_size(self):
        # todo
        pass

    def build(self) -> BaseMedia:
        return TextPlusMedia(**self.to_dict())

    @property
    def font(self) -> str:
        return self._font

    @font.setter
    def font(self, font: str) -> None:
        self._font = font

    @property
    def text_size(self) -> int:
        return self._text_size

    @text_size.setter
    def text_size(self, text_size: int) -> None:
        """
        字体大小，单位像素。由宽度和高度组成，宽高各占两个字符。如 0808、3232，
        999999，对应的字体大小是 8、32、999。

        :param text_size:
        :return:
        """
        size_str = str(text_size)
        self._text_size = int(f'{size_str}{size_str}')

    @property
    def font_style(self) -> str:
        return self._font_style

    @font_style.setter
    def font_style(self, font_style: str) -> None:
        self._font_style = font_style

    @property
    def horizontal_alignment(self) -> str:
        return self._horizontal_alignment

    @horizontal_alignment.setter
    def horizontal_alignment(self, horizontal_alignment: str) -> None:
        self._horizontal_alignment = horizontal_alignment

    @property
    def vertical_alignment(self) -> str:
        return self._vertical_alignment

    @vertical_alignment.setter
    def vertical_alignment(self, vertical_alignment: str) -> None:
        self._vertical_alignment = vertical_alignment

    @property
    def line_space(self) -> int:
        return self._line_space

    @line_space.setter
    def line_space(self, line_space: int) -> None:
        self._line_space = line_space

    @property
    def word_space(self) -> int:
        return self._word_space

    @word_space.setter
    def word_space(self, word_space: int) -> None:
        self._word_space = word_space

    @property
    def text_color(self) -> str:
        return self._text_color

    @text_color.setter
    def text_color(self, text_color: str) -> None:
        self._text_color = text_color

    @property
    def background_color(self) -> str:
        return self._background_color

    @background_color.setter
    def background_color(self, background_color: str) -> None:
        self._background_color = background_color

    @property
    def play_effect(self) -> str:
        return self._play_effect

    @play_effect.setter
    def play_effect(self, play_effect: str) -> None:
        self._play_effect = play_effect

    @property
    def effect_speed(self) -> str:
        return self._effect_speed

    @effect_speed.setter
    def effect_speed(self, effect_speed: str) -> None:
        self._effect_speed = effect_speed

    @property
    def play_count(self) -> int:
        return self._play_count

    @play_count.setter
    def play_count(self, play_count: int) -> None:
        self._play_count = play_count

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, text: str) -> None:
        self._text = text

    @property
    def is_play_text_voice(self) -> str:
        return self._is_play_text_voice

    @is_play_text_voice.setter
    def is_play_text_voice(self, is_play_text_voice: str) -> None:
        self._is_play_text_voice = is_play_text_voice

    @property
    def is_sync_play(self) -> str:
        return self._is_sync_play

    @is_sync_play.setter
    def is_sync_play(self, is_sync_play: str) -> None:
        self._is_sync_play = is_sync_play

    @property
    def voice_sound(self) -> str:
        return self._voice_sound

    @voice_sound.setter
    def voice_sound(self, voice_sound: str) -> None:
        self._voice_sound = voice_sound

    @property
    def volume(self) -> int:
        return self._volume

    @volume.setter
    def volume(self, volume: int) -> None:
        self._volume = volume

    @property
    def voice_speed(self) -> int:
        return self._voice_speed

    @voice_speed.setter
    def voice_speed(self, voice_speed: int) -> None:
        self._voice_speed = voice_speed

    @property
    def intonation(self) -> int:
        return self._intonation

    @intonation.setter
    def intonation(self, intonation: int) -> None:
        self._intonation = intonation
