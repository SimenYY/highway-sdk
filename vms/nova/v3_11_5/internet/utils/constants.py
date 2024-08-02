#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass


@dataclass(frozen=True)
class NovaOkRsp:
    # 发送文件名
    FILE_NAME_OK_RSP = b'\xAA\xFF\xFF\x12\x01\xCC\xA1\xB4'
    # 发送文件内容
    FILE_CONTENT_OK_RSP = b'\xAA\xFF\xFF\x14\x01\x00\x01\xCC\x91\xC4'
    # 指定播放
    PLAY_LIST_OK_RSP = b'\xAA\xFF\xFF\x1C\x01\xCC\xBA\xA4'


@dataclass(frozen=True)
class NovaWhat:
    """
    指令码
    注：
    1. req表示发送，rsp表示回复
    """

    # 获取当前内容
    GET_PLAYING_ITEM_REQ = b'\x2D'
    GET_PLAYING_ITEM_RSP = b'\x2E'
    # 获取当前列表
    GET_PLAYING_ALL_REQ = b'\x3A'
    GET_PLAYING_ALL_RSP = b'\x3B'

    # 发送文件名
    FILE_NAME_REQ = b'\x11'
    FILE_NAME_RSP = b'\x12'

    # 发送文件内容
    FILE_CONTENT_REQ = b'\x13'
    FILE_CONTENT_RSP = b'\x14'

    # 指定文件名播放
    PLAY_LIST_REQ = b'\x1B'
    PLAY_LIST_RSP = b'\x1C'

    # 获取当前截图
    SCREENSHOT_REQ = b'\x80'
    SCREENSHOT_RSP = b'\x81'

    # 获取屏幕高宽
    SCREEN_WIDTH_HEIGHT_REQ = b'\x82'
    SCREEN_WIDTH_HEIGHT_RSP = b'\x83'
