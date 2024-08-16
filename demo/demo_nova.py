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

# 发送播放表
with NovaClient("localhost") as client:
    # 创建媒体
    text_plus_builder = TextPlusMediaBuilder()
    text_plus_builder.text = "hello world"

    # 先获取屏幕点阵参数
    ret = client.get_device_size()
    if ret is not None:
        w, h = ret
        text_plus_builder.width = w
        text_plus_builder.height = h

    text_plus_builder.auto_adjust_text_size()

    # 创建页面item
    item_builder = ItemBuilder()
    item_builder.add_media_builder(text_plus_builder)

    # 创建播放表
    play_builder = PlayBuilder()
    play_builder.add_item_builder(item_builder)

    # 生成播放表内容， 设置播放表，
    content = play_builder.set_play_id(1).build().create_msg()

    client.set_play_list(content)

# 发送查询设备点阵大小
# cli = NovaClient("localhost")
# cli.make_connection()
# w, h = cli.get_device_size()
# cli.close_connection()
