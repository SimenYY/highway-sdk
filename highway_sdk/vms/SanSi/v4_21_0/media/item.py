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
:Time: 2024/8/22 9:59
"""

from pydantic import BaseModel, Field

from .media import Media


class Item(BaseModel):
    media: Media
    duration: int = Field(..., ge=2, le=30000)
    screen_in: int

    def create_msg(self) -> str:
        protocol = (f'{self.duration},'
                    f'{self.screen_in},'
                    f'0,')
        protocol += self.media.create_msg()

        return protocol
