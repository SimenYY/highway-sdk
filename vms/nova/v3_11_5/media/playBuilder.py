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
:Time: 2024/7/31 17:13
:Department: 公路机电工程技术中心
:Copyright: ©1993-2023 浙江中控信息产业股份有限公司
"""
from typing import List

from .itemBuilder import Item, ItemBuilder
from .play import Play


class PlayBuilder:
    def __init__(self):
        # 播放节目集合
        self.item_list: List[Item] = []
        # 播放节目对应的直接指令
        self._push_protocol: str = ''
        # 节目id
        self._play_id: int = 1

    def add_item_builder(self, builder: ItemBuilder) -> 'PlayBuilder':
        item = builder.build()
        self.item_list.append(item)

        return self

    def build(self) -> Play:
        return Play(self)

    @property
    def push_protocol(self) -> str:
        return self._push_protocol

    @push_protocol.setter
    def push_protocol(self, push_protocol: str) -> None:
        self._push_protocol = push_protocol

    @property
    def play_id(self) -> int:
        return self._play_id

    def set_play_id(self, play_id: int) -> 'PlayBuilder':
        self._play_id = play_id
        return self
