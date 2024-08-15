#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:FileName: exceptions.py
:Project:
:Brand:
:Version:
:Description: 
:Author: He YinYu
:Link:
:Time: 2024/8/8 11:22
"""


class ValidationError(Exception):
    """
    数据校验引发的异常信息
    """

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class ResponseError(Exception):
    """
    响应异常
    """

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class CrcError(Exception):
    """
    校验异常
    """

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class ProtocolParserError(Exception):
    """
    协议解析异常
    """

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class HostResponseTimeoutError(Exception):
    """
    主机响应超时
    """

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class InvalidSocketError(Exception):
    """
    无效的socket
    """

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message
