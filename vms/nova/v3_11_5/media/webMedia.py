#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:FileName: webMedia.py.py
:Project:
:Brand:
:Version:
:Description: 
:Author: He YinYu
:Link:
:Time: 2024/8/1 19:12
:Department: 公路机电工程技术中心
:Copyright: ©1993-2023 浙江中控信息产业股份有限公司
"""
from .baseMedia import BaseMedia


class WebMedia(BaseMedia):

    def __init__(self, builder):
        super().__init__(builder)
        self.url: str = builder.url
        self.refresh_time: int = builder.refresh_time

    def create_protocol(self) -> str:
        protocol = (f'webview{self.index}='
                    f'{self.x},'
                    f'{self.y},'
                    f'{self.url},'
                    f'{self.refresh_time},'
                    f'{self.width},'
                    f'{self.height}')
        return protocol


