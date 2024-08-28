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


class Client:
    # 响应超时时间
    rsp_timeout: int = 3
    # 接受字节流大小单位
    buf_size: int = 1024

    def __init__(self, ip: str, port: int):
        """
        不合法的通信地址要让实例一开始就不成立
        """
        validate_ipv4_address(ip)
        validate_port(port)

        self.ip: str = ip
        self.port: int = port
        self._sock: Optional[socket.socket] = None

    def __enter__(self):
        self.make_connection()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_connection()
        if exc_type is not None:
            logger.error(f'{self.log_prefix()} {exc_type} {exc_val} {exc_tb}')
        # 抑制异常
        return True

    @property
    def sock(self) -> socket.socket:
        return self._sock

    @sock.setter
    def sock(self, sock: socket.socket):
        self._sock = sock

    def make_connection(self):
        if self._sock is not None:
            return

        try:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._sock.settimeout(self.rsp_timeout)
            self._sock.connect((self.ip, self.port))
        except (TimeoutError, ConnectionRefusedError, Exception) as e:
            logger.error(f'{self.log_prefix()} {e}')
            self.close_connection()

    def close_connection(self):
        if self._sock is not None:
            self._sock.close()
            self._sock = None

    def log_prefix(self) -> str:
        return f'{self.ip}:{self.port}'
