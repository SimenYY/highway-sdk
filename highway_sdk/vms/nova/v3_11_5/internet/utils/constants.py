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
    SEND_FILE_NAME_RSP = b'\x12'

    # 发送文件内容
    SEND_FILE_CONTENT_REQ = b'\x13'
    SEND_FILE_CONTENT_RSP = b'\x14'

    # 文件发送完毕
    FILE_SEND_END_RSP = b'\xF9'

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

    # 获取开关屏状态
    GET_SCREEN_SWITCH_STATUS_REQ = b'\xBA'
    GET_SCREEN_SWITCH_STATUS_RSP = b'\xBA'


def get_success_rsp(rsp_what: bytes) -> bytes | None:
    """
    成功响应，响应固定
    :param rsp_what:
    :return: bytes
    """
    match rsp_what:
        case NovaWhat.SEND_FILE_NAME_RSP:
            return b'\xAA\xFF\xFF\x12\x01\xCC\xA1\xB4'
        case NovaWhat.SEND_FILE_CONTENT_RSP:
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
        case NovaWhat.SEND_FILE_NAME_RSP:
            return len(get_success_rsp(NovaWhat.SEND_FILE_NAME_RSP))
        case NovaWhat.SEND_FILE_CONTENT_RSP:
            return len(get_success_rsp(NovaWhat.SEND_FILE_CONTENT_RSP))
        case NovaWhat.PLAY_LIST_RSP:
            return len(get_success_rsp(NovaWhat.PLAY_LIST_RSP))
        case _:
            return None


@dataclass(frozen=True)
class NovaTagsConvertor:
    COLOR_TO_PLATFORM = {
        '4': '1',  # 黄
        '1': '2',  # 红
        '2': '3',  # 绿
    }

    PLATFORM_TO_COLOR = {
        '1': '4',  # 黄
        '2': '1',  # 红
        '3': '2',  # 绿
    }

    PLATFORM_TO_FONT = {
        '107': '2',  # 楷体
        '115': '3',  # 宋体
        '104': '1',  # 黑体
        '102': '4',  # 仿宋
    }

    FONT_TO_PLATFORM = {
        '2': '107',  # 楷体
        '3': '115',  # 宋体
        '1': '104',  # 黑体
        '4': '102',  # 仿宋
    }
