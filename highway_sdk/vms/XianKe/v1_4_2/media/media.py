#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:FileName: txtMedia.py
:Project:
:Brand:
:Version:
:Description: 
:Author: He YinYu
:Link:
:Time: 2025/2/18 14:20
"""
from pydantic import BaseModel, Field

from enum import Enum


class FontEnum(str, Enum):
    HEI_TI = 'h'
    KAI_TI = 'k'
    SONG_TI = 's'
    FANG_SONG = 'f'


class TextSizeEnum(int, Enum):
    SIZE_16 = 16
    SIZE_24 = 24
    SIZE_32 = 32
    SIZE_48 = 48
    SIZE_64 = 64


class ColorEnum(str, Enum):
    RED = '255000000000'
    GREEN = '000255000000'
    YELLOW = '255255000000'
    BLACK = '000000000000'


class Media(BaseModel):
    x: int = Field(..., ge=-99, le=999)
    y: int = Field(..., ge=-99, le=999)
    font: FontEnum
    text_size: TextSizeEnum
    text_color: ColorEnum
    background_color: ColorEnum
    text: str
    bmg_file_name: str

    def __str__(self):
        protocol = (f"\\C{self.x:03d}{self.y:03d}"
                    f"\\F{self.font}{self.text_size}"
                    f"\\T{self.text_color}"
                    f"\\B{self.background_color}")

        if self.text_size:
            protocol += f"\\U{self.text}"
        else:
            protocol += f"\\I{self.bmg_file_name.rjust(3, '0')}"

        return protocol


class MediaBuilder:

    def __init__(self):
        self.x: int = 0
        self.y: int = 0
        self.font: str = FontEnum.HEI_TI.value
        self.text_size: int = TextSizeEnum.SIZE_16.value
        self.text_color: str = ColorEnum.YELLOW.value
        self.background_color: str = ColorEnum.BLACK.value
        self.text: str | None = None
        self.bmg_file_name: str | None = None

    def build(self) -> Media:
        """
        构造函数

        :return:
        """
        return Media(**self.__dict__)
