#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .baseMedia import BaseMedia
from .baseBuilder import BaseBuilder


class BaseMediaBuilder(BaseBuilder):

    def __init__(self):
        # 从 1 开始
        self._index: int = 0
        # x坐标
        self._x: int = 0
        # y坐标
        self._y: int = 0
        # 显示宽度
        self._width: int = 0
        # 显示高度
        self._height: int = 0
        # 停留时间
        self._duration: int = 0

    def build(self) -> BaseMedia:
        pass

    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, index: int) -> None:
        self._index = index

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
    def width(self) -> int:
        return self._width

    @width.setter
    def width(self, width: int) -> None:
        self._width = width

    @property
    def height(self) -> int:
        return self._height

    @height.setter
    def height(self, height: int) -> None:
        self._height = height

    @property
    def duration(self) -> int:
        return self._duration

    @duration.setter
    def duration(self, duration: int) -> None:
        self._duration = duration

