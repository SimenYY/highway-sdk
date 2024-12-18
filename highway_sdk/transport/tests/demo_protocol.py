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
from highway_sdk.transport.protocol import ClusterReconnectClientFactory
from twisted.internet.protocol import Protocol
from highway_sdk.core.logx import logger
from highway_sdk.transport import driver


class MyProtocol(Protocol):

    def connectionMade(self):
        addr = self.transport.getPeer()
        logger.success(f'{addr} connected')


if __name__ == '__main__':
    ip_list = [
        '127.0.0.1'
    ]
    port = 8888

    driver.run(
        factory=ClusterReconnectClientFactory.set_protocol(MyProtocol),
        ip_list=ip_list,
        port=port,
    )
