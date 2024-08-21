#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:FileName: media.py.py
:Project:
:Brand:
:Version:
:Description: 
:Author: He YinYu
:Link:
:Time: 2024/8/20 13:53
"""
from .enums import ColorEnum, FontEnum, TextSizeEnum
from pydantic import BaseModel, Field, field_validator


class Media(BaseModel):
    x: int = Field(..., ge=0, le=999)
    y: int = Field(..., ge=0, le=999)
    bmp_file_name: str
    png_file_name: str
    jpg_file_name: str
    gif_file_name: str
    text_color: ColorEnum
    background_color: ColorEnum
    word_space: int = Field(..., ge=0, le=99)
    font: FontEnum
    text_size: TextSizeEnum
    text: str

    def create_msg(self):
        protocol = (fr'\C{self.x:03d}{self.y:03d}'
                    fr'\F{self.font}{self.text_size}'
                    fr'\T{self.text_color}'
                    fr'\K{self.background_color}')
        if self.word_space != 0:
            protocol += fr'\M{self.word_space:02d}'

        protocol += fr'\W{self.text}'
        return protocol
