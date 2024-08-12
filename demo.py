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
from highway_sdk.vms.nova.v3_11_5.playManager import PlayManager
from highway_sdk.vms.nova.v3_11_5.media import PlayBuilder, ItemBuilder, TextMediaBuilder
from highway_sdk.vms.nova.v3_11_5.internet.novaClient import NovaClient

t = TextMediaBuilder()

print(t.build().create_msg())


