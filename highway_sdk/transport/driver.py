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
        factory: Type[TcpClientFactory],
        ip_list: list,
        port: int
) -> None:

    for ip in ip_list:
        reactor.connectTCP(ip, port, factory)
    reactor.run()
