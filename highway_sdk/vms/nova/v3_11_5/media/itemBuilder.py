#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import List

from .baseMediaBuilder import BaseMedia, BaseMediaBuilder
from .item import Item
from .baseBuilder import BaseBuilder
import copy


class ItemBuilder(BaseBuilder):

    def __init__(self):
        self.media_list: List[BaseMedia] = []

        # item内媒体序号，默认从0开始，自动累加，不应该被修改
        self._auto_media_index: int = 0

        # 停留时间， 默认单位是100ms
        self._duration: int = 100
        # 入屏方式
        self._screen_in: str = '1'
        # 出屏方式
        self._screen_out: str = '1'
        # 入屏速度
        self._screen_speed: str = '1'
        # 闪烁速度
        self._flash_speed: str = '0'
        # 闪烁次数
        self._flash_count: str = '5'
        # 播放次数
        self._play_count: str = '1'

    def add_media_builder(self, media_builder: BaseMediaBuilder) -> 'ItemBuilder':
        """
        可在此处扩展公共参数，每个媒体的私有参数，请在创建媒体build的时候扩展

        :param media_builder:
        :return:
        """
        self._auto_media_index += 1
        media_builder.index = self._auto_media_index
        media_builder.duration = self.duration
        self.media_list.append(media_builder.build())

        return self

    def build(self):
        return Item(**self.to_dict())

    @property
    def duration(self) -> int:
        return self._duration

    @duration.setter
    def duration(self, duration: int):
        self._duration = duration

    @property
    def index(self) -> int:
        return self._auto_media_index

    @index.setter
    def index(self, index: int):
        self._auto_media_index = index

    @property
    def screen_in(self) -> str:
        return self._screen_in

    @screen_in.setter
    def screen_in(self, screen_in: str):
        self._screen_in = screen_in

    @property
    def screen_out(self) -> str:
        return self._screen_out

    @screen_out.setter
    def screen_out(self, screen_out: str):
        self._screen_out = screen_out

    @property
    def screen_speed(self) -> str:
        return self._screen_speed

    @property
    def flash_speed(self) -> str:
        return self._flash_speed

    @flash_speed.setter
    def flash_speed(self, flash_speed: str):
        self._flash_speed = flash_speed

    @property
    def flash_count(self) -> str:
        return self._flash_count

    @flash_count.setter
    def flash_count(self, flash_count: str):
        self._flash_count = flash_count

    @property
    def play_count(self) -> str:
        return self._play_count

    @play_count.setter
    def play_count(self, play_count: str):
        self._play_count = play_count
