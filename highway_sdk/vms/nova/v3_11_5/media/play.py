#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import List
from pydantic import BaseModel, Field
from .item import Item


class Play(BaseModel):
    """
    表示每一个完整的play文件内容
    """

    item_list: List[Item]
    push_protocol: str
    # 支持播放列表1-100
    play_id: int = Field(..., gt=0, le=100)

    def create_msg(self) -> str:
        """
        play播放文件字符串
        """
        if not self.item_list:
            raise ValueError('item_list is empty')

        protocol = ['[all]', '\n', f'items={len(self.item_list)}', '\n']

        for item in self.item_list:
            protocol.append(item.create_msg())
            protocol.append('\n')
        return ''.join(protocol[:-1])  # 去掉最后一个换行符
