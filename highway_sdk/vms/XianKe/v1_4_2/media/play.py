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
:Time: 2025/2/18 13:47
"""
from typing import List

from pydantic import BaseModel

from highway_sdk.vms.XianKe.v1_4_2.media.item import Item, ItemBuilder


class Play(BaseModel):
    item_list: List[Item]

    def __str__(self):
        """
        注：除了转义字符，其他字符均大小写无关

        :return:
        """
        protocol = '[LIST]'
        protocol += '\r\n'
        protocol += f'ItemCount={len(self.item_list):03d}'
        protocol += '\r\n'
        for i, item in enumerate(self.item_list):
            protocol += f"Item{i:02d}={item}"
            protocol += '\r\n'

        return protocol


class PlayBuilder:
    """
    Usage::

        >>> from highway_sdk.vms.XianKe.v1_4_1.media.media import MediaBuilder
        >>> from highway_sdk.vms.XianKe.v1_4_1.media.item import ItemBuilder
        >>> mb = MediaBuilder()
        >>> mb.text = "文本测试"
        >>> ib = ItemBuilder()
        >>> ib.media = mb.build()
        >>> pb = PlayBuilder()
        >>> pb.add_item_builder(ib)
        >>> print(str(pb.build()))
        [LIST]
        ItemCount=001
        Item00=10,1,0,1,1,\\C000000\\Fh16\\T255255000000\\B000000000000\\U文本测试
    """

    def __init__(self):
        self.item_list: List[Item] = []

    def add_item_builder(self, builder: ItemBuilder) -> 'PlayBuilder':
        """
        添加item建造器

        :param builder: 建造器
        :return:
        :rtype: PlayBuilder
        """
        self.item_list.append(builder.build())
        return self

    def build(self) -> Play:
        """
        构造函数

        :return: Play
        """
        return Play(**self.__dict__)
