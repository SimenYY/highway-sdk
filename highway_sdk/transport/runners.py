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
from typing import Type

from twisted.internet import reactor

from .tcpClient import TcpClientFactory


def run(
        factory: TcpClientFactory,
        port: int,
        ip_list: list,
        debug: bool = False
) -> None:
    if debug:
        reactor.connectTCP('localhost', port, factory)
    else:
        for ip in ip_list:
            reactor.connectTCP(ip, port, factory)
    reactor.run()
