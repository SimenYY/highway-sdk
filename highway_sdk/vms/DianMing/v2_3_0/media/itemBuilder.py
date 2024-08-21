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
:Time: 2024/8/20 13:53
"""
from typing import List, Optional
from .item import Item
from .media import Media
from .mediaBuilder import MediaBuilder
from .baseBuilder import BaseBuilder


class ItemBuilder(BaseBuilder):
    def __init__(self):
        self.media: Optional[Media] = None
        # 单位是十分之一s
        self._duration: int = 100
        self._screen_in: str = '0'
        self._screen_out: str = '0'

    def build(self):
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
