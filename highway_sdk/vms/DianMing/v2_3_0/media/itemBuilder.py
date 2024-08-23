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
from typing import Optional

from .baseBuilder import BaseBuilder
from .item import Item
from .media import Media
from .mediaBuilder import MediaBuilder


class ItemBuilder(BaseBuilder):
    def __init__(self):
        self.media: Optional[Media] = None
        # 单位是十分之一s
        self._duration: int = 100
        self._screen_in: int = 0
        self._screen_out: int = 0

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
