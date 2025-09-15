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
:Time: 2025/4/17 10:33
"""
from abc import ABC, abstractmethod
from typing import List
from highway_sdk.vms.SanSi.v4_21_0.media.play import Play, MultipleWinPlay, SingleWinPlay
from highway_sdk.vms.SanSi.v4_21_0.media.win import Win
from highway_sdk.vms.SanSi.v4_21_0.media import WinBuilder

__all__ = [
    "MultipleWinPlayBuilder",
    "SingleWinPlayBuilder",
]


class PlayBuilder(ABC):
    @abstractmethod
    def build(self) -> Play:
        pass


class MultipleWinPlayBuilder(PlayBuilder):
    """
    >>> from highway_sdk.vms.SanSi.v4_21_0.media import TextBuilder, ItemBuilder, WinBuilder, MultipleWinPlayBuilder
    >>> tb = TextBuilder("Hello World!")
    >>> ib = ItemBuilder(tb.build())
    >>> wb = WinBuilder().add_item_builder(ib)
    >>> mwp = MultipleWinPlayBuilder().add_win_builder(wb)
    >>> print(str(mwp.build()).replace("\\r\\n", "\\n")[:-1])
    [playlist]
    nwindows=1
    windows0_x=None
    windows0_y=None
    windows0_w=None
    windows0_h=None
    item_no=1
    item0=1000,1,0,\\C000000\\fh1616\\c255255000000\\b000000000000\\S00Hello World!

    """

    def __init__(self):
        self.win_list: List[Win] = []

    def build(self) -> MultipleWinPlay:
        return MultipleWinPlay(**self.__dict__)

    def add_win_builder(self, builder: WinBuilder) -> "MultipleWinPlayBuilder":
        self.win_list.append(builder.build())

        return self


class SingleWinPlayBuilder(PlayBuilder):
    """

    >>> from highway_sdk.vms.SanSi.v4_21_0.media import TextBuilder, ItemBuilder, WinBuilder, SingleWinPlayBuilder
    >>> tb = TextBuilder("Hello World!")
    >>> ib = ItemBuilder(tb.build())
    >>> wb = WinBuilder().add_item_builder(ib)
    >>> swp = SingleWinPlayBuilder(wb.build())
    >>> print(str(swp.build()).replace("\\r\\n", "\\n")[:-1])
    [playlist]
    item_no=1
    item0=1000,1,0,\\C000000\\fh1616\\c255255000000\\b000000000000\\S00Hello World!

    """

    def __init__(self, win: Win):
        self.win = win

    def build(self) -> SingleWinPlay:
        return SingleWinPlay(**self.__dict__)


if __name__ == '__main__':
    import doctest

    doctest.testmod()
