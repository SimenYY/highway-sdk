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
from typing import Type, List, Callable, Optional

from twisted.internet.address import IPv4Address
from twisted.internet.protocol import Protocol, ReconnectingClientFactory
from twisted.internet.task import LoopingCall
from twisted.python.failure import Failure

from .strategy import RecvStrategy
from ..core.logx import logger
from ..interface.iot import MqttClient


class TcpClient(Protocol):
    # 轮询时间
    polling_interval = 5
    # 随机抖动因子
    jitter = 0.119626565582
    # 数据接受策略
    recv_strategy: Type[RecvStrategy] = None

    # 设备产品型号
    series: str = 'unknown'

    def __init__(self):
        self.addr: IPv4Address | None = None

    @property
    def sn(self) -> str:
        return f'{self.series}_{self.addr.host}'

    def connectionMade(self):
        logger.success(f"Connection is established {self.log_addr()}.")
        self.addr = self.transport.getPeer()

    def dataReceived(self, data: bytes) -> None:
        logger.debug(f'Receive from {self.log_addr()}: {data.hex(" ")}')

    def log_addr(self):
        if self.transport:
            addr = self.transport.getPeer()
            return f'{addr.host}:{addr.port}'
        else:
            return 'None:None'

    def looping_call_tasks(self, tasks: List[Callable[[], None]]):
        """
        执行定时任务

        :param tasks:
        :return:
        """
        for task in tasks:
            loop = LoopingCall(task)

            if len(tasks) > 1:
                interval = random.normalvariate(self.polling_interval,
                                                self.polling_interval * self.jitter)
            else:
                interval = self.polling_interval

            loopDeferred = loop.start(interval, now=False)

            loopDeferred.addErrback(self.eb_loop_failed)
            loopDeferred.addCallback(self.cb_loop_done)

    def eb_loop_failed(self, failure: Failure):
        """
        在循环任务失败时调用
        """
        pass

    def cb_loop_done(self, result):
        """
        在循环任务完成时调用
        """
        pass

    def send(self, data: bytes) -> None:
        if self.transport:
            logger.debug(f'Send to {self.log_addr()}: {data.hex(" ")}')
            self.transport.write(data)
        else:
            logger.error(f'Send failed, transport is None.')
            return


class TcpClientFactory(ReconnectingClientFactory):
    protocol = TcpClient
    # 最大重连时间
    maxDelay = 10
    # 延时因子
    factor = 1.6180339887498948

    def __init__(self, protocol: Optional[Callable[[], Protocol]] = None):
        if protocol is not None:
            self.protocol = protocol

    def clientConnectionLost(self, connector, unused_reason) -> None:
        addr = connector.getDestination()
        logger.critical(f"Connection is lost {addr.host}:{addr.port}. reason: {unused_reason}")
        return super().clientConnectionLost(connector, unused_reason)

    def clientConnectionFailed(self, connector, reason) -> None:
        addr = connector.getDestination()
        logger.critical(f"Connection is lost {addr.host}:{addr.port}. reason: {reason}")
        return super().clientConnectionLost(connector, reason)


class IotMqttMixin:
    mqtt_client: Optional[MqttClient] = None

    def startFactory(self):
        logger.info("Start connecting to MQTT Broker......")
        self.mqtt_client.connect()