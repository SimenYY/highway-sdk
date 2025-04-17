#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:FileName: media.py
:Project:
:Brand:
:Version:
:Description: 
:Author: He YinYu
:Link:
:Time: 2025/4/16 16:34
"""
from pydantic import BaseModel, Field

from .enums import ColorEnum, FontEnum, TextSizeEnum


class Media(BaseModel):
    x: int = Field(..., ge=0, le=999)
    y: int = Field(..., ge=0, le=999)


class Text(Media):
    text_color: ColorEnum
    background_color: ColorEnum
    word_space: int = Field(..., ge=0, le=99)
    font: FontEnum
    text_size: TextSizeEnum
    text: str

    def __str__(self):
        protocol = (f"\\C{self.x:03d}{self.y:03d}"
                    f"\\f{self.font}{self.text_size}"
                    f"\\c{self.text_color}"
                    f"\\b{self.background_color}"
                    f"\\S{self.word_space:02d}"
                    f"{self.text}")
        return protocol


class Bmp(Media):
    bmp_file_name: str

    def __str__(self):
        protocol = (f"\\C{self.x:03d}{self.y:03d}"
                    f"\\B{self.bmp_file_name}")
        return protocol


class Png(Media):
    png_file_name: str

    def __str__(self):
        protocol = (f"\\C{self.x:03d}{self.y:03d}"
                    f"\\P{self.png_file_name}")
        return protocol


class Jpg(Media):
    jpg_file_name: str

    def __str__(self):
        protocol = (f"\\C{self.x:03d}{self.y:03d}"
                    f"\\J{self.jpg_file_name}")
        return protocol


class Gif(Media):
    gif_file_name: str

    def __str__(self):
        protocol = (f"\\C{self.x:03d}{self.y:03d}"
                    f"\\G{self.gif_file_name}")
        return protocol


class Mpg(Media):
    """
    video
    """
    mpg_file_name: str

    def __str__(self):
        protocol = (f"\\C{self.x:03d}{self.y:03d}"
                    f"\\M{self.mpg_file_name}")
        return protocol






