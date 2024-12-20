#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:FileName: test_protocol.py
:Project:
:Brand:
:Version:
:Description: 
:Author: He YinYu
:Link:
:Time: 2024/12/18 13:23
"""
from highway_sdk.transport.strategy import HeaderLengthStrategy
from highway_sdk.transport.protocol import ClusterReconnectClientFactory, ClientProtocol
from highway_sdk.core.logx import logger
from highway_sdk.transport import driver
from highway_sdk.transport.protocol import Protocol
from twisted.internet.tcp import Client


class MyProtocol(ClientProtocol):

    def connectionMade(self) -> None:
        super().connectionMade()

        self.recv_strategy = HeaderLengthStrategy(b'#', 4)
        self.looping_call_tasks([self.task_ask, self.task_query])

    def task_query(self):
        self.send(b'hello, world')

    def task_ask(self):
        pass
        # self.send(b'are you ok')


if __name__ == '__main__':
    ip_list = [
        '127.0.0.1',
        '172.20.61.88'
    ]
    port = 8888

    driver.run(
        factory=ClusterReconnectClientFactory.set_protocol(MyProtocol),
        ip_list=ip_list,
        port=port,
    )
