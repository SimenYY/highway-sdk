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
:Time: 2024/8/22 9:21
"""
from typing import List
from .winBuilder import WinBuilder
from .itemBuilder import ItemBuilder
from .baseBuilder import BaseBuilder
from .play import Play
from .win import Win
from .item import Item


class PlayBuilder(BaseBuilder):

    def __init__(self):
        self.win_or_item_list: List[Win | Item] = []

    def build(self):
        return Play(**self.to_dict())

    def add_win_or_item_builder(self, builder: WinBuilder | ItemBuilder):
        self.win_or_item_list.append(builder.build())
        return self

