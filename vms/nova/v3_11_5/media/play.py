#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import List

from .item import Item


class Play:

    def __init__(self, builder):
        self.item_list: List[Item] = builder.item_list
        self.push_protocol: str = builder.push_protocol
        self.play_id: int = builder.play_id

    def create_protocol(self) -> str:
        """
        当前默认按照全部更新，后续如果需要，则修改

        :return:
        """
        if not self.item_list:
            raise ValueError('item_list is empty')

        protocol = ['[all]', '\n', f'items={len(self.item_list)}', '\n']
        for i, item in enumerate(self.item_list):
            protocol.append(f'[item{i}]')
            protocol.append('\n')
            protocol.append(item.create_protocol())
            protocol.append('\n')
        return ''.join(protocol[:-1])  # 去掉最后一个换行符
