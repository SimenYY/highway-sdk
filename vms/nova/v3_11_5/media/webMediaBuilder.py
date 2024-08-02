#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .baseMedia import BaseMedia
from .baseMediaBuilder import BaseMediaBuilder


class WebMediaBuilder(BaseMediaBuilder):

    def __init__(self):
        super().__init__()
        self._url: str = ''
        # 单位100ms 为0时不刷新
        self._refresh_time: int = 0

    def build(self) -> BaseMedia:
        pass

    @property
    def url(self) -> str:
        return self._url

    @url.setter
    def url(self, url: str) -> None:
        self._url = url

    @property
    def refresh_time(self) -> int:
        return self._refresh_time

    @refresh_time.setter
    def refresh_time(self, refresh_time: int) -> None:
        self._refresh_time = refresh_time
