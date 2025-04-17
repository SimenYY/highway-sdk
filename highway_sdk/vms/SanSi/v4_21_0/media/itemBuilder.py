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
:Time: 2025/4/17 10:31
"""

from .enums import ScreenInEnum
from .media import Media
from .item import Item

__all__ = [
    'ItemBuilder'
]


class ItemBuilder:
    def __init__(self, media: Media):
        self.media = media
        # 单位为百分之一秒， 缺省为2
        self.duration: int = 1000
        # 缺省为0
        self.screen_in: int = ScreenInEnum.NORMAL.value
        # 播放速度
        self.play_speed: int = 0

    def build(self) -> Item:
        return Item(**self.__dict__)


