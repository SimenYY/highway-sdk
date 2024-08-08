#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import List

from .item import Item


class Play:
    """
    表示每一个完整的play文件内容
    """
    def __init__(self, builder):
        self.item_list: List[Item] = builder.item_list
        self.push_protocol: str = builder.push_protocol
        self.play_id: int = builder.play_id

    def __str__(self) -> str:
        """
        play播放文件字符串
        """
        if not self.item_list:
            raise ValueError('item_list is empty')

        protocol = ['[all]', '\n', f'items={len(self.item_list)}', '\n']
        for i, item in enumerate(self.item_list):
            protocol.append(f'[item{i}]')
            protocol.append('\n')
            protocol.append(item.__str__())
            protocol.append('\n')
        return ''.join(protocol[:-1])  # 去掉最后一个换行符
