#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:FileName: baseMediaBuilder.py
:Project:
:Brand:
:Version:
:Description: 
:Author: He YinYu
:Link:
:Time: 2024/7/31 13:26
:Department: 公路机电工程技术中心
:Copyright: ©1993-2023 浙江中控信息产业股份有限公司
"""
from abc import ABC, abstractmethod
from .baseMedia import BaseMedia


class BaseMediaBuilder(ABC):

    def __init__(self):
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

    @abstractmethod
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

