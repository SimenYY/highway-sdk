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
:Time: 2024/8/22 9:59
"""
from typing import Literal, overload

from .enums import ColorEnum, FontEnum, TextSizeEnum
from pydantic import BaseModel, Field


class Media(BaseModel):
    x: int = Field(..., ge=-99, le=999)
    y: int = Field(..., ge=-99, le=999)
    bmp_file_name: str
    png_file_name: str
    jpg_file_name: str
    gif_file_name: str
    mpg_file_name: str
    text_color: ColorEnum
    background_color: ColorEnum
    word_space: int = Field(..., ge=0, le=99)
    font: FontEnum
    text_size: TextSizeEnum
    text: str

    def create_msg(self):
        if self.text != '':
            return self._create_text_msg()
        elif self.bmp_file_name != '':
            return self._create_pic_msg()
        elif self.mpg_file_name != '':
            return self._create_video_msg()
        elif self.jpg_file_name != '':
            return self._create_pic_msg('jpg')
        elif self.png_file_name != '':
            return self._create_pic_msg('png')
        elif self.gif_file_name != '':
            return self._create_pic_msg('gif')
        else:
            # 默认
            return self._create_text_msg()

    def _create_text_msg(self):
        protocol = ''
        if self.x != 0 or self.y != 0:
            protocol += fr'\C{self.x:03d}{self.y:03d}'

        protocol += (fr'\f{self.font}{self.text_size}'
                     fr'\c{self.text_color}')
        # 等于缺省值就不加上了
        if self.background_color != ColorEnum.BLACK.value:
            protocol += fr'\b{self.background_color}'

        if self.word_space != 0:
            protocol += fr'\S{self.word_space:02d}'

        protocol += self.text
        return protocol

    def _create_pic_msg(self, pic_type: Literal['bmp', 'png', 'jpg', 'gif'] = 'bmp'):
        protocol = ''
        if self.x != 0 or self.y != 0:
            protocol += fr'\C{self.x:03d}{self.y:03d}'

        match pic_type:
            case 'bmp':
                protocol += fr'\B{self.bmp_file_name}'
            case 'png':
                protocol += fr'\P{self.png_file_name}'
            case 'jpg':
                protocol += fr'\J{self.jpg_file_name}'
            case 'gif':
                protocol += fr'\G{self.gif_file_name}'
            case _:
                raise ValueError('pic_type must be bmp, png, jpg or gif')

        return protocol

    def _create_video_msg(self, video_type: Literal['mpg'] = 'mpg'):
        protocol = ''
        if self.x != 0 or self.y != 0:
            protocol += fr'\C{self.x:03d}{self.y:03d}'

        match video_type:
            case 'mpg':
                protocol += fr'\M{self.mpg_file_name}'
            case _:
                raise ValueError('video_type must be mpg')

        return protocol
