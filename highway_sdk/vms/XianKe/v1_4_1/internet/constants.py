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


@dataclass(frozen=True)
class XianKeTagsConvertor:
    COLOR_TO_PLATFORM = {
        '255255000000': '1',  # 黄
        '255000000000': '2',  # 红
        '000255000000': '3',  # 绿
    }

    PLATFORM_TO_COLOR = {
        '1': '255255000000',  # 黄
        '2': '255000000000',  # 红
        '3': '000255000000',  # 绿
    }

    PLATFORM_TO_FONT = {
        '104': 'k',  # 楷体
        '107': 's',  # 宋体
        '102': 'h',  # 黑体
        '115': 'f',  # 仿宋
    }

    FONT_TO_PLATFORM = {
        'h': '102',  # 黑体
        'k': '104',  # 楷体
        's': '107',  # 宋体
        'f': '115',  # 仿宋
    }