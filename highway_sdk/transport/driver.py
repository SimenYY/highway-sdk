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


def run(
        factory: TcpClientFactory,
        ip_list: list,
        port: int
) -> None:

    if hasattr(factory.__class__, 'init'):
        factory.__class__.init()

    for ip in ip_list:
        reactor.connectTCP(ip, port, factory)
    reactor.run()
