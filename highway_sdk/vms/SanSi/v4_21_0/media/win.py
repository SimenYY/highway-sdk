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
:Time: 2024/8/22 10:26
"""
from typing import List

from pydantic import BaseModel
from .item import Item


class Win(BaseModel):
    item_list: List[Item]
    x: int
    y: int
    w: int
    h: int

    def create_msg(self):
        protocol = f'item_no={len(self.item_list)}'
        protocol += '\n'
        for i, item in enumerate(self.item_list):
            protocol += f'item{i}={item.create_msg()}'
            protocol += '\n'

        return protocol.rstrip('\n')
