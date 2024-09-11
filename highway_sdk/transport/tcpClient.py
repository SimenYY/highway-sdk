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
:Time: 2024/9/11 14:55
"""
import random
from typing import Optional, Type, List, Callable

from twisted.internet.interfaces import IAddress
from twisted.internet.task import LoopingCall
from twisted.internet.protocol import Protocol, ReconnectingClientFactory
from ..core.logx import logger


class TcpClient(Protocol):
    MAX_LENGTH = 16384

    polling_interval = 5

    jitter = 0.119626565582

    def __init__(self):
        # 缓冲区
        self._buffer: bytes = b''
        # 分隔符
        self.delimiter: bytes = b'\r\n'

    def connectionMade(self):
        addr = self.transport.getPeer()
        logger.success(f"Connection is established {addr.host}:{addr.port}.")

    def dataReceived(self, data: bytes) -> None:
        self._buffer += data

    def clear_buffer(self):
        self._buffer = b''

    def looping_call_tasks(self, tasks: List[Callable[[], None]]):
        interval = random.normalvariate(self.polling_interval,
                                        self.polling_interval * self.jitter)
        for task in tasks:
            loop = LoopingCall(task)
            loopDeferred = loop.start(interval)


class TcpClientFactory(ReconnectingClientFactory):
    protocol = TcpClient
    # 最大重连时间，这个范围内波动
    maxDelay = 10

    def __init__(self, protocol: Type[Protocol] | None = None):
        if protocol is not None:
            self.protocol = protocol

    def buildProtocol(self, addr: IAddress) -> "Optional[Protocol]":
        return super().buildProtocol(addr)

    def clientConnectionLost(self, connector, unused_reason) -> None:
        addr = connector.getDestination()
        logger.critical(f"Connection is lost {addr.host}:{addr.port}. reason: {unused_reason}")
        return super().clientConnectionLost(connector, unused_reason)

    def clientConnectionFailed(self, connector, reason) -> None:
        addr = connector.getDestination()
        logger.critical(f"Connection is lost {addr.host}:{addr.port}. reason: {reason}")
        return super().clientConnectionLost(connector, reason)
