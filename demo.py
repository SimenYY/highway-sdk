#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:FileName: demo.py
:Project:
:Brand:
:Version:
:Description: 
:Author: He YinYu
:Link:
:Time: 2024/8/8 15:46
"""
from highway_sdk.vms.nova.v3_11_5.internet.novaClient import NovaClient
from highway_sdk.vms.nova.v3_11_5.media import PlayBuilder, ItemBuilder, TextPlusMediaBuilder

text_plus_builder = TextPlusMediaBuilder()
text_plus_builder.text = '文本测试'

item_builder = ItemBuilder()
item_builder.add_media_builder(text_plus_builder)
play_builder = PlayBuilder()
play_builder.add_item_builder(item_builder)

cli = NovaClient('127.0.0.1')

with cli.connect() as connection:
    if connection:
        connection.get_device_size()