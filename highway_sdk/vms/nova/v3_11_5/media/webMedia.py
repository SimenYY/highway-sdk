#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .baseMedia import BaseMedia


class WebMedia(BaseMedia):

    def __init__(self, builder):
        super().__init__(builder)
        self.url: str = builder.url
        self.refresh_time: int = builder.refresh_time

    def __str__(self) -> str:
        protocol = (f'webview{self.index}='
                    f'{self.x},'
                    f'{self.y},'
                    f'{self.url},'
                    f'{self.refresh_time},'
                    f'{self.width},'
                    f'{self.height}')
        return protocol


