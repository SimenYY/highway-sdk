#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:FileName: winBuilder.py
:Project:
:Brand:
:Version:
:Description: 
:Author: He YinYu
:Link:
:Time: 2024/8/22 10:26
"""
from typing import List
from .itemBuilder import ItemBuilder
from .baseBuilder import BaseBuilder
from .item import Item
from .win import Win


class WinBuilder(BaseBuilder):

    def __init__(self):
        self.item_list: List[Item] = []
        self._x: int = 0
        self._y: int = 0
        self._w: int = 0
        self._h: int = 0

    def build(self):
        return Win(**self.to_dict())

    def add_item_builder(self, builder: ItemBuilder):
        self.item_list.append(builder.build())
        return self

    @property
    def x(self) -> int:
        return self._x

    @x.setter
    def x(self, x: int) -> None:
        self._x = x

    @property
    def y(self) -> int:
        return self._y

    @y.setter
    def y(self, y: int) -> None:
        self._y = y

    @property
    def w(self) -> int:
        return self._w

    @w.setter
    def w(self, w: int) -> None:
        self._w = w

    @property
    def h(self) -> int:
        return self._h

    @h.setter
    def h(self, h: int) -> None:
        self._h = h