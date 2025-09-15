#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:FileName: winPlay.py
:Project:
:Brand:
:Version:
:Description: 
:Author: He YinYu
:Link:
:Time: 2025/4/17 10:34
"""
from typing import List

from .item import Item
from .itemBuilder import ItemBuilder
from .win import Win

__all__ = [
    "WinBuilder"
]


class WinBuilder:

    def __init__(self):
        self.item_list: List[Item] = []
        self.x: int | None = None
        self.y: int | None = None
        self.w: int | None = None
        self.h: int | None = None

    def build(self) -> Win:
        return Win(**self.__dict__)

    def add_item_builder(self, builder: ItemBuilder) -> "WinBuilder":
        self.item_list.append(builder.build())

        return self
