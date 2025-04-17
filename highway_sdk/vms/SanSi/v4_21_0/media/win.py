#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:FileName: win.py
:Project:
:Brand:
:Version:
:Description: 
:Author: He YinYu
:Link:
:Time: 2025/4/16 16:34
"""
from typing import List

from pydantic import BaseModel
from .item import Item


class Win(BaseModel):
    item_list: List[Item]
    x: int | None
    y: int | None
    w: int | None
    h: int | None

    def __str__(self):
        line_break = "\r\n"
        protocol = f'item_no={len(self.item_list)}'
        protocol += line_break
        for i, item in enumerate(self.item_list):
            protocol += f'item{i}={item}'
            protocol += line_break

        return protocol
