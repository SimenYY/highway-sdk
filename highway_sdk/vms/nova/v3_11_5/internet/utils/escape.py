#!/usr/bin/env python
# -*- coding: utf-8 -*-


class NovaEscape:
    """
    对发送报文，接受报文进行转义
    """

    @staticmethod
    def byte_to_short(data: bytes) -> bytes:
        data = data.replace(b'\xEE', b'\xEE\x0E')
        data = data.replace(b'\xAA', b'\xEE\x0A')
        data = data.replace(b'\xCC', b'\xEE\x0C')

        return data

    @staticmethod
    def short_to_byte(data: bytes) -> bytes:
        data = data.replace(b'\xEE\x0A', b'\xAA')
        data = data.replace(b'\xEE\x0C', b'\xCC')
        data = data.replace(b'\xEE\x0E', b'\xEE')
        return data
