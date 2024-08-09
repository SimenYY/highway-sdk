#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .baseMedia import BaseMedia
from pydantic import HttpUrl


class WebMedia(BaseMedia):

    url: HttpUrl
    refresh_time: int

    def create_msg(self) -> str:
        protocol = (f'webview{self.index}='
                    f'{self.x},'
                    f'{self.y},'
                    f'{self.url},'
                    f'{self.refresh_time},'
                    f'{self.width},'
                    f'{self.height}')
        return protocol


