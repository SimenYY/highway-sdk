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
:Time: 2025/4/16 16:34
"""

from pydantic import BaseModel, Field

from .media import Media


class Item(BaseModel):
    media: Media
    duration: int = Field(..., ge=2, le=30000)
    screen_in: int
    play_speed: int

    def __str__(self):
        protocol = (f"{self.duration},"
                    f"{self.screen_in},"
                    f"{self.play_speed},"
                    f"{self.media}")
        return protocol



