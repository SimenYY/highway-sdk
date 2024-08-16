#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:FileName: demo_nova.py
:Project:
:Brand:
:Version:
:Description: 
:Author: He YinYu
:Link:
:Time: 2024/8/16 13:24
"""
import socket

from highway_sdk.vms.nova.v3_11_5.internet.novaClient import NovaClient
from highway_sdk.vms.nova.v3_11_5.media import PlayBuilder, ItemBuilder, TextPlusMediaBuilder

# 创建媒体
text_plus_builder = TextPlusMediaBuilder()
text_plus_builder.text = "hello world"

# 创建页面item
item_builder = ItemBuilder()
item_builder.add_media_builder(text_plus_builder)

# 创建播放表
play_builder = PlayBuilder()
play_builder.add_item_builder(item_builder)

# 生成播放表内容
content = play_builder.set_play_id(1).build().create_msg()

# 发送方法1
with NovaClient("localhost") as client:
    client.set_play_list(content)

# 发送方法2
cli = NovaClient("localhost")
cli.make_connection()
cli.get_device_size()
cli.close_connection()
