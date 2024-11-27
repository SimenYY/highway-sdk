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
:Time: 2024/8/22 9:20
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class SanSiWhat:
    # 获取当前内容
    GET_NOW_PLAY_CONTENT = b'\x39\x37'

    # 上载文件
    SEND_FILE_NAME_AND_CONTENT = b'\x31\x30'

    # 播放播放表
    PLAY_LIST = b'\x39\x38'

    # 设置当前显示亮度
    SET_NOW_BRIGHTNESS = b'\x30\x35'

    # 取当前显示亮度和调节方式
    GET_NOW_BRIGHTNESS = b'\x30\x36'


@dataclass(frozen=True)
class SansiTagsConvertor:
    PLATFORM_TO_COLOR = {
        '1': '255185000000',  # 黄
        '2': '255000000000',  # 红
        '3': '000255000000',  # 绿
    }

    COLOR_TO_PLATFORM = {
        '255185000000': '1',  # 黄
        '255000000000': '2',  # 红
        '000255000000': '3',  # 绿
    }

    PLATFORM_TO_FONT = {
        '104': 'k',  # 楷体
        '107': 's',  # 宋体
        '102': 'h',  # 黑体
        '115': 'f',  # 仿宋
    }

    FONT_TO_PLATFORM = {
        'k': '104',  # 楷体
        's': '107',  # 宋体
        'h': '102',  # 黑体
        'f': '115',  # 仿宋
    }
