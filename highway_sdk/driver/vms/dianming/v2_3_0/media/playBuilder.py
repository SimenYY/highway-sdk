#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:FileName: playBuilder.py
:Project:
:Brand:
:Version:
:Description: 
:Author: He YinYu
:Link:
:Time: 2024/8/20 13:53
"""
from typing import List
from .baseBuilder import BaseBuilder
from .item import Item
from .itemBuilder import ItemBuilder
from .play import Play


class PlayBuilder(BaseBuilder):
    def __init__(self):
        self.item_list: List[Item] = []
        # 默认播放表文件名 play00.lst
        self._play_id: int = 0

    def add_item_builder(self, builder: ItemBuilder):
        self.item_list.append(builder.build())
        return self

    def build(self) -> Play:
        return Play(**self.to_dict())

    @property
    def play_id(self) -> int:
        return self._play_id

    def set_play_id(self, play_id: int) -> 'PlayBuilder':
        self._play_id = play_id
        return self
