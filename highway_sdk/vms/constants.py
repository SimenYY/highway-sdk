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
:Time: 2024/11/21 11:27
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class DeviceReturnCode:
    SUCCESS = 0
    SOCKET_ERROR = -1
    HOST_RESPONSE_TIMEOUT = -2
    HOST_RESPONSE_ERROR = -3
    PROTOCOL_PARSER_ERROR = -4
    CLIENT_REQUEST_ERROR = -5
    INVALID_INPUT = -98
    UNKNOWN_ERROR = -99

    # 映射返回码到描述
    CODE_TO_DESCRIPTION = {
        SUCCESS: "成功",
        SOCKET_ERROR: "套接字错误",
        HOST_RESPONSE_TIMEOUT: "主机响应超时",
        HOST_RESPONSE_ERROR: "主机响应错误",
        PROTOCOL_PARSER_ERROR: "协议解析错误",
        CLIENT_REQUEST_ERROR: "客户端请求错误",
        INVALID_INPUT: "无效输入",
        UNKNOWN_ERROR: "未知错误"
    }

    @classmethod
    def get_desc(cls, code):
        """获取返回码的描述"""
        return cls.CODE_TO_DESCRIPTION.get(code, "错误码未定义")
