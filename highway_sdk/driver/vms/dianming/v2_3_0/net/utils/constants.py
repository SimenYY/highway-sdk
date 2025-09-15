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
:Time: 2024/8/20 14:03
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class DmWhat:
    """
    指令码
    """

    # 获取当前内容
    GET_NOW_PLAY_CONTENT_REQ = b'\x37\x33'
    GET_NOW_PLAY_CONTENT_RSP = b'\x37\x34'

    # 播放列表下发并立即显示
    SEND_PLAY_LIST_AND_PLAY_REQ = b'\x37\x31'
    SEND_PLAY_LIST_AND_PLAY_RSP = b'\x37\x32'


@dataclass(frozen=True)
class DmReturnCode:
    SUCCESS = 0
    SOCKET_ERROR = -1
    HOST_RESPONSE_TIMEOUT = -2
    HOST_RESPONSE_ERROR = -3
    PROTOCOL_PARSER_ERROR = -4
    CLIENT_REQUEST_ERROR = -5
    UNKNOWN_ERROR = -99
