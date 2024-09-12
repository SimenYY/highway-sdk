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

    @buffer.setter
    def buffer(self, value: bytes) -> None:
        self._buffer = value

    def receive(self, data: bytes) -> List[bytes]:
        raise NotImplementedError


class DelimiterStrategy(RecvStrategy):
    """
    根据分隔符去筛选报文
    """

    def __init__(self, delimiter: bytes = b'\r\n'):
        super().__init__()

        self.delimiter = delimiter

    def receive(self, data: bytes) -> List[bytes]:
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

    def receive(self, data: bytes) -> List[bytes]:
        self._buffer += data
        messages = []
        while True:
            start = self._buffer.find(self.header)
            if start == -1:
                break
            end = self._buffer.find(self.footer, start + len(self.header))
            if end == -1:
                break
            messages.append(self._buffer[start: end + 1])
            self._buffer = self._buffer[end + 1:]
        return messages


class HeaderLengthStrategy(RecvStrategy):
    """
    根据报文头，长度来筛选报文
    """

    def __init__(self, header: bytes, length: int):
        super().__init__()
        self.header = header
        self.length = length

    def receive(self, data: bytes) -> List[bytes]:
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
