#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:FileName: constants.py
:Project:
:Brand:
:Version:
:Description: 
:Author: He YinYu
:Link:
:Time: 2025/2/17 14:05
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class XianKeResCode:
    SUCCESS: bytes = b'\x01'
    FAILURE: bytes = b'\x00'


@dataclass(frozen=True)
class XianKeWhat:
    # 获取当前内容
    GET_NOW_PLAY_CONTENT = b'\x32\x34'
    # 获取当前列表
    GET_NOW_PLAY_ALL_CONTENT = b'\x32\x33'
    # 发送文件内容
    upload_file = b'\x32\x30'
    # 播放播放表
    PLAY_LIST = b'\x32\x32'
    # 获取当前亮度
    GET_NOW_BRIGHTNESS = b'\x30\x35'
