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
