#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:FileName: runners.py
:Project:
:Brand:
:Version:
:Description: 
:Author: He YinYu
:Link:
:Time: 2024/9/20 9:48
"""

from twisted.internet import reactor

from .tcpClient import TcpClientFactory

from typing import Type


def run(
        factory: TcpClientFactory | Type[TcpClientFactory],
        ip_list: list,
        port: int
) -> None:
    if isinstance(factory, type):
        for ip in ip_list:
            # 一个工厂对于一个协议，这样重连的超时时间是分开的
            reactor.connectTCP(ip, port, factory())
    else:
        for ip in ip_list:
            reactor.connectTCP(ip, port, factory)
    reactor.run()
