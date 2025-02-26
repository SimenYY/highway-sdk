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

import asyncio
from asyncio import StreamReader, StreamWriter


from highway_sdk.core.log import logger
from highway_sdk.core.validators import (
    validate_ipv4_address,
    validate_port,
)


class BaseClient:
    """基础类
    """
    # 接受字节流大小单位
    buffer_size: int = 1024
    # 超时时间
    timeout: int = 3

    def __init__(self, host: str, port: int):
        validate_ipv4_address(host)
        validate_port(port)

        self.host = host
        self.port = port

    @property
    def log_addr(self) -> str:
        """日志地址

        :return: 
        :rtype: str
        """
        return f'{self.host}:{self.port}'


class Client(BaseClient):
    """TCP客户端
    """
    # 响应超时时间
    rsp_timeout: int = 3

    def __init__(self, host: str, port: int):
        super().__init__(host, port)
        self._sock: Optional[socket.socket] = None
        self._connected = False

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        if exc_type is not None:
            logger.error('%s %s %s %s', self.log_addr, exc_type, exc_val, exc_tb)
        return True

    @property
    def sock(self) -> socket.socket:
        """获取套接字

        :return: 
        :rtype: socket.socket
        """
        return self._sock

    @sock.setter
    def sock(self, sock: socket.socket):
        self._sock = sock

    def connect(self) -> None:
        """
        建立连接

        :raise socket.error:
        :return:
        """
        if self._sock is not None:
            return

        try:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._sock.settimeout(self.rsp_timeout)
            self._sock.connect((self.host, self.port))
            self._connected = True
        except socket.error as e:
            logger.error('%s %s', self.log_addr, e)
            self.close()
            raise e

    def close(self):
        """连接关闭

        """
        if self._sock is not None:
            self._sock.close()
            self._sock = None
            self._connected = False

    def send(self, data: bytes, debug: bool = False, log_prefix: str = '') -> None:
        """

        :raise socket.error:
        :param data:
        :param debug:
        :param log_prefix:
        :return:
        """
        if not self._connected:
            raise socket.error(f'Not connected to {self.log_addr} server')

        self._sock.sendall(data)

        if debug:
            logger.debug('%s - Send to %s: %s', log_prefix, self.log_addr, data.hex(" "))

    def recv(self, buffer_size: int, debug: bool = False, log_prefix: str = '') -> bytes:
        """

        :param buffer_size:
        :param debug:
        :param log_prefix:
        :return:
        """
        if not self._connected:
            raise socket.error(f'Not connected to {self.log_addr} server')

        data = self._sock.recv(buffer_size)

        if not data:
            raise socket.error(f'{self.log_addr} No data received')

        if debug:
            logger.debug('%s - Received from %s: %s', log_prefix, self.log_addr, data.hex(" "))

        return data


class AsyncClient(BaseClient):
    """异步TCP客户端

    :param BaseClient: 
    :type BaseClient: 
    """

    def __init__(self, host: str, port: int):
        super().__init__(host, port)
        self.reader: Optional[StreamReader] = None
        self.writer: Optional[StreamWriter] = None

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
        if exc_type is not None:
            logger.error('%s %s %s %s', self.log_addr, exc_type, exc_val, exc_tb)
        return True

    async def connect(self) -> bool:
        """连接函数

        :return: 
        :rtype: bool
        """
        ret = True
        try:
            self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
        except ConnectionRefusedError as e:
            logger.error('%s %s', self.log_addr, e)
            await self.close()
            ret = False
        return ret

    async def send(self, data: bytes, **kwargs) -> None:
        """

        :param data:
        :param debug:
        :param log_prefix:
        :return:
        """
        if self.writer is None:
            raise IOError(f"Not connected to {self.log_addr} server")
        self.writer.write(data)
        await self.writer.drain()
        
        log_prefix = kwargs.get('log_prefix', '')
        logger.debug('%s - Send to %s: %s', log_prefix, self.log_addr, data.hex(" "))

    async def recv(self) -> bytes:
        """
        :raise IOError
        :return:
        """
        if self.reader is None:
            raise IOError(f"Not connected to {self.log_addr} server")
        data = await self.read_timeout()
        return data

    async def read_timeout(self) -> bytes:
        """
        带有超时的读取函数

        :raise TimeoutError
        :raise IOError
        :return:
        """
        if self.reader is None:
            raise IOError(f"Not connected to {self.log_addr} server")
        try:
            res = await asyncio.wait_for(
                self.reader.read(self.buffer_size),
                self.timeout
            )
        except asyncio.TimeoutError as exc:
            raise asyncio.TimeoutError(f'read_timeout timeout >{self.timeout}s !') from exc

        return res

    async def close(self):
        """连接关闭
        """
        if self.writer is not None:
            self.writer.close()
            await self.writer.wait_closed()
