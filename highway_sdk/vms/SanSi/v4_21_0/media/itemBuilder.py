#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:FileName: itemBuilder.py
:Project:
:Brand:
:Version:
:Description: 
:Author: He YinYu
:Link:
:Time: 2024/8/22 9:21
"""
from typing import List, Optional
from .item import Item
from .media import Media
from .mediaBuilder import MediaBuilder
from .baseBuilder import BaseBuilder
from .enums import ScreenInEnum


class ItemBuilder(BaseBuilder):
    def __init__(self):
        self.media: Optional[Media] = None
        # 单位为百分之一秒， 缺省为2
        self._duration: int = 1000
        # 缺省为0
        self._screen_in: int = ScreenInEnum.NORMAL.value

    def build(self) -> Item:
        return Item(**self.to_dict())

    def add_media_builder(self, builder: MediaBuilder):
        self.media = builder.build()
        return self

    @property
    def duration(self) -> int:
        return self._duration

    @duration.setter
    def duration(self, duration: int) -> None:
        self._duration = duration

    @property
    def screen_in(self) -> int:
        return self._screen_in

    @screen_in.setter
    def screen_in(self, screen_in: int) -> None:
        self._screen_in = screen_in



