#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:FileName: play.py
:Project:
:Brand:
:Version:
:Description: 
:Author: He YinYu
:Link:
:Time: 2024/8/20 13:51
"""
from pydantic import BaseModel, Field
from .item import Item
from typing import List


class Play(BaseModel):
    item_list: List[Item]
    # 支持播放列表1-100
    play_id: int = 0

    def create_msg(self) -> str:
        if not self.item_list:
            raise ValueError('item_list is empty')

        protocol = ['[PLAYLIST]', '\r\n', f'ITEM_NO={len(self.item_list):03d}', '\r\n']
        for i, item in enumerate(self.item_list):
            protocol.append(f'ITEM{i:03d}={item.create_msg()}')
            protocol.append('\r\n')
        return ''.join(protocol[:-1])  # 去掉最后一个\r\n
