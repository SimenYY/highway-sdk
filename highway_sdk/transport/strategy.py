#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:FileName: recvStrategy.py
:Project:
:Brand:
:Version:
:Description: 
:Author: He YinYu
:Link:
:Time: 2024/9/12 10:09
"""
from typing import List


class RecvStrategy:
    # 最大接收数据包长度
    MAX_LENGTH = 16384

    def __init__(self):
        self._buffer: bytes = b''

    @property
    def buffer(self) -> bytes:
        return self._buffer

    def recv(self, data: bytes) -> List[bytes]:
        raise NotImplementedError

    def clear_buffer(self):
        self._buffer = b''


class DelimiterStrategy(RecvStrategy):
    """
    根据分隔符去筛选报文
    """

    def __init__(self, delimiter: bytes = b'\r\n'):
        super().__init__()

        self.delimiter = delimiter

    def recv(self, data: bytes) -> List[bytes]:
        if len(self._buffer) >= self.MAX_LENGTH:
            self.clear_buffer()

        self._buffer += data
        messages = []
        while self._buffer:
            try:
                message, self._buffer = self._buffer.split(self.delimiter, maxsplit=1)
                messages.append(message)
            except ValueError:
                break
        return messages


class HeaderFooterStrategy(RecvStrategy):
    """
    根据报文头、报文尾去筛选报文
    """

    def __init__(self, header: bytes, footer: bytes):
        super().__init__()
        self.header = header
        self.footer = footer

    def recv(self, data: bytes) -> List[bytes]:
        if len(self._buffer) >= self.MAX_LENGTH:
            self.clear_buffer()

        self._buffer += data
        messages = []
        while True:
            start = self._buffer.find(self.header)
            if start == -1:
                break
            end = self._buffer.find(self.footer, start + len(self.header))
            if end == -1:
                break
            messages.append(self._buffer[start: end + len(self.footer)])
            self._buffer = self._buffer[end + len(self.footer):]
        return messages


class HeaderFooterExtraStrategy(RecvStrategy):
    """
    例如Nova的报文
    报文头--中间数据--报文尾--额外校验码
    """

    def __init__(self, header: bytes, footer: bytes, extra_len: int):
        super().__init__()
        self.header = header
        self.footer = footer
        self.extra_len = extra_len

    def recv(self, data: bytes) -> List[bytes]:
        if len(self._buffer) >= self.MAX_LENGTH:
            self.clear_buffer()

        self._buffer += data
        messages = []
        while True:
            start = self._buffer.find(self.header)
            if start == -1:
                break
            end = self._buffer.find(self.footer, start + len(self.header))
            if end == -1:
                break
            extra = self._buffer[end + len(self.footer):]
            if len(extra) < self.extra_len:
                break
            messages.append(self._buffer[start: end + len(self.footer) + self.extra_len])
            self._buffer = self._buffer[end + len(self.footer) + self.extra_len:]
        return messages


class HeaderLengthStrategy(RecvStrategy):
    """
    根据报文头，长度来筛选报文
    """

    def __init__(self, header: bytes, length: int):
        super().__init__()
        self.header = header
        self.length = length

    def recv(self, data: bytes) -> List[bytes]:
        if len(self._buffer) >= self.MAX_LENGTH:
            self.clear_buffer()

        self._buffer += data
        messages = []
        while True:
            start = self._buffer.find(self.header)
            if start == -1:
                break
            if len(self._buffer[start:]) < self.length:
                break
            messages.append(self._buffer[start: start + self.length])
            self._buffer = self._buffer[start + self.length:]

        return messages
