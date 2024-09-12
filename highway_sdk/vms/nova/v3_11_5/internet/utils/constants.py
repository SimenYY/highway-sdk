#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass


@dataclass(frozen=True)
class NovaWhat:
    """
    指令码
    注：
    1. req表示发送，rsp表示回复
    """

    # 获取当前内容
    GET_NOW_PLAY_CONTENT_REQ = b'\x2D'
    GET_NOW_PLAY_CONTENT_RSP = b'\x2E'
    # 获取当前列表
    GET_NOW_PLAY_ALL_CONTENT_REQ = b'\x3A'
    GET_NOW_PLAY_ALL_CONTENT_RSP = b'\x3B'

    # 发送文件名
    SEND_FILE_NAME_REQ = b'\x11'
    FILE_NAME_RSP = b'\x12'

    # 发送文件内容
    SEND_FILE_CONTENT_REQ = b'\x13'
    FILE_CONTENT_RSP = b'\x14'

    # 指定文件名播放
    PLAY_LIST_REQ = b'\x1B'
    PLAY_LIST_RSP = b'\x1C'

    # 获取当前截图
    SCREENSHOT_REQ = b'\x80'
    SCREENSHOT_RSP = b'\x81'

    # 获取屏幕高宽
    GET_DEVICE_SIZE_REQ = b'\x82'
    GET_DEVICE_SIZE_RSP = b'\x83'

    # 获取当前亮度
    GET_NOW_BRIGHTNESS_REQ = b'\xC3'
    GET_NOW_BRIGHTNESS_RSP = b'\xC3'


def get_success_rsp(rsp_what: bytes) -> bytes | None:
    """
    成功响应，响应固定
    :param rsp_what:
    :return: bytes
    """
    match rsp_what:
        case NovaWhat.FILE_NAME_RSP:
            return b'\xAA\xFF\xFF\x12\x01\xCC\xA1\xB4'
        case NovaWhat.FILE_CONTENT_RSP:
            return b'\xAA\xFF\xFF\x14\x01\x00\x01\xCC\x91\xC4'
        case NovaWhat.PLAY_LIST_RSP:
            return b'\xAA\xFF\xFF\x1C\x01\xCC\xBA\xA4'
        case _:
            return None


def get_success_rsp_len(rsp_what: bytes) -> int | None:
    """
    成功响应，长度固定
    :param rsp_what:
    :return: int
    """
    match rsp_what:
        case NovaWhat.GET_DEVICE_SIZE_RSP:
            return 10
        case NovaWhat.FILE_NAME_RSP:
            return len(get_success_rsp(NovaWhat.FILE_NAME_RSP))
        case NovaWhat.FILE_CONTENT_RSP:
            return len(get_success_rsp(NovaWhat.FILE_CONTENT_RSP))
        case NovaWhat.PLAY_LIST_RSP:
            return len(get_success_rsp(NovaWhat.PLAY_LIST_RSP))
        case _:
            return None


@dataclass(frozen=True)
class NovaReturnCode:
    SUCCESS = 0
    SOCKET_ERROR = -1
    HOST_RESPONSE_TIMEOUT = -2
    HOST_RESPONSE_ERROR = -3
    PROTOCOL_PARSER_ERROR = -4
    CLIENT_REQUEST_ERROR = -5
    UNKNOWN_ERROR = -99
