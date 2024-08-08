#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import List
from pydantic import BaseModel, NonNegativeInt
from .item import Item


class Play(BaseModel):
    """
    表示每一个完整的play文件内容
    """

    item_list: List[Item]
    push_protocol: str
    play_id: NonNegativeInt

    def create_msg(self) -> str:
        """
        play播放文件字符串
        """
        if not self.item_list:
            raise ValueError('item_list is empty')

        protocol = ['[all]', '\n', f'items={len(self.item_list)}', '\n']
        for i, item in enumerate(self.item_list):
            protocol.append(f'[item{i}]')
            protocol.append('\n')
            protocol.append(item.create_msg())
            protocol.append('\n')
        return ''.join(protocol[:-1])  # 去掉最后一个换行符
