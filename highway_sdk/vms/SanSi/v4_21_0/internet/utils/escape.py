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
:Time: 2024/8/22 9:21
"""


class SanSiEscape:
    """
    对发送报文，接受报文进行转义
    """

    @staticmethod
    def byte_to_short(data: bytes) -> bytes:
        data = data.replace(b'\x1B', b'\x1B\x00')
        data = data.replace(b'\x02', b'\x1B\xE7')
        data = data.replace(b'\x03', b'\x1B\xE8')

        return data

    @staticmethod
    def short_to_byte(data: bytes) -> bytes:
        data = data.replace(b'\x1B\xE7', b'\x02')
        data = data.replace(b'\x1B\xE8', b'\x03')
        data = data.replace(b'\x1B\x00', b'\x1B')

        return data
