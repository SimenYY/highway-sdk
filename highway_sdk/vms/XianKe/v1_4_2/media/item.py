#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:FileName: item.py
:Project:
:Brand:
:Version:
:Description: 
:Author: He YinYu
:Link:
:Time: 2025/2/18 13:47
"""
from pydantic import BaseModel, Field
from enum import Enum

from highway_sdk.vms.XianKe.v1_4_2.media.media import Media, MediaBuilder


class ScreenInOutEnum(int, Enum):
    NORMAL = 1
    MOVE_UP = 6
    MOVE_DOWN = 7
    MOVE_LEFT = 8
    MOVE_RIGHT = 9


class Item(BaseModel):
    # 停留时间
    duration: int
    # 进入方式
    screen_in: ScreenInOutEnum
    # 显示效果
    play_effect: int
    # 出屏方式
    screen_out: ScreenInOutEnum
    # 播放速度
    play_speed: int = Field(..., gt=0)
    # 媒体内容
    media: Media

    def __str__(self):
        protocol = (f"{self.duration},"
                    f"{self.screen_in},"
                    f"{self.play_effect},"
                    f"{self.screen_out},"
                    f"{self.play_speed},"
                    f"{self.media}")
        return protocol


class ItemBuilder:

    def __init__(self):
        self.media: Media = MediaBuilder().build()

        self.duration: int = 10
        self.screen_in: int = ScreenInOutEnum.NORMAL.value
        self.screen_out: int = ScreenInOutEnum.NORMAL.value
        self.play_effect: int = 0
        self.play_speed: int = 1

    def build(self) -> Item:
        """
        构造函数

        :return:
        """
        return Item(**self.__dict__)
