#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:FileName: client.py
:Project:
:Brand:
:Version:
:Description: 
:Author: He YinYu
:Link:
:Time: 2024/8/21 10:39
"""
import socket
from typing import Optional

from loguru import logger
from highway_sdk.core.validators import (
    validate_ipv4_address,
    validate_port,
)
import asyncio
from asyncio import StreamReader, StreamWriter


class Client:
    # 响应超时时间
    rsp_timeout: int = 3
    # 接受字节流大小单位
    buf_size: int = 1024

    def __init__(self, host: str, port: int):
        """
        不合法的通信地址要让实例一开始就不成立
        """
        validate_ipv4_address(host)
        validate_port(port)

        self.host: str = host
        self.port: int = port
        self._sock: Optional[socket.socket] = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        if exc_type is not None:
            logger.error(f'{self.log_addr()} {exc_type} {exc_val} {exc_tb}')
        # 抑制异常
        return True

    @property
    def sock(self) -> socket.socket:
        return self._sock

    @sock.setter
    def sock(self, sock: socket.socket):
        self._sock = sock

    def connect(self):
        if self._sock is not None:
            return

        try:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._sock.settimeout(self.rsp_timeout)
            self._sock.connect((self.host, self.port))
        except (TimeoutError, ConnectionRefusedError, Exception) as e:
            logger.error(f'{self.log_addr()} {e}')
            self.close()

    def close(self):
        if self._sock is not None:
            self._sock.close()
            self._sock = None

    def log_addr(self) -> str:
        return f'{self.host}:{self.port}'


class AsyncClient:
    # 接受字节流大小单位
    buf_size: int = 1024

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.reader: StreamReader | None = None
        self.writer: StreamWriter | None = None

    async def connect(self) -> bool:
        ret = True
        try:
            self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
        except ConnectionRefusedError as e:
            logger.error(f'{self.log_addr()} {e}')
            await self.close()
            ret = False
        return ret

    async def send(self, msg: bytes):
        if self.writer is None:
            raise Exception("Not connected to server")
        self.writer.write(msg)
        await self.writer.drain()

    async def recv(self) -> bytes:
        if self.reader is None:
            raise Exception("Not connected to server")
        data = await self.reader.read(self.buf_size)
        return data

    async def close(self):
        if self.writer is not None:
            self.writer.close()
            await self.writer.wait_closed()

    def log_addr(self) -> str:
        return f'{self.host}:{self.port}'
