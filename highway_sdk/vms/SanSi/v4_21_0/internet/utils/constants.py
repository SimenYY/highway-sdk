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
class SanSiReturnCode:
    SUCCESS = 0
    SOCKET_ERROR = -1
    HOST_RESPONSE_TIMEOUT = -2
    HOST_RESPONSE_ERROR = -3
    PROTOCOL_PARSER_ERROR = -4
    CLIENT_REQUEST_ERROR = -5
    UNKNOWN_ERROR = -99
