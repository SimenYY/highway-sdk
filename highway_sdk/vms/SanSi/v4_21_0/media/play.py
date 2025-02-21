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
:Time: 2024/8/22 9:59
"""
from typing import List

from pydantic import BaseModel

from .item import Item
from .win import Win


class Play(BaseModel):
    win_or_item_list: List[Win | Item]

    def create_msg(self):
        if not self.win_or_item_list:
            raise ValueError('win_or_item_list is empty')

        win_or_item = self.win_or_item_list[0]

        if isinstance(win_or_item, Win):
            return self._create_multiple_msg()
        elif isinstance(win_or_item, Item):
            return self._create_single_msg()
        else:
            raise TypeError('win_or_item_list must be Win or Item')

    def _create_multiple_msg(self) -> str:
        protocol = '[playlist]'
        protocol += '\n'
        protocol += f'nwindows={len(self.win_or_item_list)}'
        protocol += '\n'
        for i, win in enumerate(self.win_or_item_list):
            protocol += f'windows{i}_x={win.x}'
            protocol += '\n'
            protocol += f'windows{i}_y={win.y}'
            protocol += '\n'
            protocol += f'windows{i}_w={win.w}'
            protocol += '\n'
            protocol += f'windows{i}_h={win.h}'
            protocol += '\n'
            protocol += win.create_msg()
            protocol += '\n'
        return protocol.rstrip('\n')

    def _create_single_msg(self) -> str:
        protocol = '[playlist]'
        protocol += '\n'
        protocol += f'item_no={len(self.win_or_item_list)}'
        protocol += '\n'
        for i, item in enumerate(self.win_or_item_list):
            protocol += f'item{i}={item.create_msg()}'
            protocol += '\n'

        return protocol.rstrip('\n')
