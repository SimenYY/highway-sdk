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
:Time: 2024/8/20 13:51
"""
from typing import List

from .media import Media
from pydantic import BaseModel, NonNegativeInt


class Item(BaseModel):
    media: Media
    duration: NonNegativeInt
    screen_in: str
    screen_out: str

    def create_msg(self) -> str:
        protocol = (f'{self.duration},'
                    f'{self.screen_in},'
                    f'0,'
                    f'{self.screen_out},'
                    f'0,')

        protocol += self.media.create_msg()

        return protocol

