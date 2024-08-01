#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:FileName: escape.py
:Project:
:Brand:
:Version:
:Description: 
:Author: He YinYu
:Link:
:Time: 2024/8/1 11:07
:Department: 公路机电工程技术中心
:Copyright: ©1993-2023 浙江中控信息产业股份有限公司
"""


class NovaEscape:
    """
    对发送报文，接受报文进行转移
    """
    @staticmethod
    def send(data: bytes) -> bytes:
        data.replace(b'\xAA', b'\xEE\x0A')
        data.replace(b'\xCC', b'\xEE\x0C')
        data.replace(b'\xEE', b'\xEE\x0E')
        return data

    @staticmethod
    def recv(data: bytes) -> bytes:
        data.replace(b'\xEE\x0A', b'\xAA')
        data.replace(b'\xEE\x0C', b'\xCC')
        data.replace(b'\xEE\x0E', b'\xEE')
        return data

