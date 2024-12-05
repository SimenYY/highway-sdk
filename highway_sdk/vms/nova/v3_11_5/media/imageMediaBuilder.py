#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:FileName: imageMediaBuilder.py
:Project:
:Brand:
:Version:
:Description: 
:Author: He YinYu
:Link:
:Time: 2024/9/3 15:35
"""
from .imageMedia import ImageMedia
from .baseMediaBuilder import BaseMediaBuilder


class ImageMediaBuilder(BaseMediaBuilder):

    def __init__(self):
        super().__init__()
        # 图片文件路径名
        self._file_path: str = ''
        # 闪烁
        self._flash: str = '0'

    def build(self):
        return ImageMedia(**self.to_dict())

    @property
    def file_path(self) -> str:
        return self._file_path

    @file_path.setter
    def file_path(self, file_path: str) -> None:
        self._file_path = file_path

    @property
    def flash(self) -> str:
        return self._flash

    @flash.setter
    def flash(self, flash: str) -> None:
        self._flash = flash
