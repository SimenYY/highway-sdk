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
import ipaddress
import random
from typing import Type, List, Callable, Optional, Any

from twisted.internet.address import IPv4Address
from twisted.internet.protocol import Protocol, ReconnectingClientFactory
from twisted.internet.task import LoopingCall
from twisted.python.failure import Failure

from .strategy import RecvStrategy
from ..core.logx import logger
from ..core.client import Client
from ..interface.iot import MqttClient, IotMqttClient


class _IotControlClientMixin:
    def iot_subscribe(self, on_message: Callable[..., None]):
        self.factory.mqtt_client.subscribe_control_req(
            series=self.series,
            sn=self.sn,
            on_message=on_message
        )

    @classmethod
    def get_topic_host(cls, topic: str) -> Optional[str]:
        """
        topic: /edge/bg/bg_127.0.0.1/1.0/data

        :param topic:
        :return:
        """
        try:
            parts = topic.split('/')
            host = parts[3].split('_')[1]
            ipaddress.IPv4Address(host)
        except Exception as e:
            logger.error(f'get_topic_host failed, {e}')
            host = None
        return host

    @classmethod
    def on_message(cls, client, userdata, message) -> None:
        """
        控制设备demo
            host = cls.get_topic_host(message.topic)
            cls.single_send(host=host, port=settings.addr.port, data=data)

        :param client:
        :param userdata:
        :param message:
        :return:
        """
        logger.info(f'接受到控制指令 - topic={message.topic}, payload={message.payload}')

    @classmethod
    def single_send(cls, host, port, data: bytes, log_prefix: str = '') -> None:
        """
        单次发送

        :param host:
        :param port:
        :param data:
        :param log_prefix:
        :return:
        """
        try:
            with Client(host=host, port=port) as client:
                client.send(data=data, log_prefix=log_prefix)
        except Exception as e:
            logger.error(f'{log_prefix} - Send failed, {e}.')


class _IotFactoryMixin:
    mqtt_client: Optional[MqttClient] = None

    @classmethod
    def init(cls) -> None:
        """

        :return:
        """
        logger.info("Start connecting to MQTT Broker......")
        cls.mqtt_client.connect()


class TcpClient(Protocol):
    """
    用于基于TCP协议的设备的客户端，具备与设备通信交互的功能

    """

    # 轮询时间
    polling_interval = 5
    # 随机抖动因子
    jitter = 0.119626565582
    # 数据接受策略
    recv_strategy: Type[RecvStrategy] = None
    # 设备产品型号
    series: Optional[str] = None

    def __init__(self):
        self.addr: Optional[IPv4Address] = None

    @property
    def sn(self) -> str:
        return f'{self.series}_{self.addr.host}'

    def connectionMade(self) -> None:
        self.addr = self.transport.getPeer()
        logger.success(f"Connection is established {self.log_addr}.")

    def dataReceived(self, data: bytes) -> None:
        logger.debug(f'Receive from {self.log_addr}: {data.hex(" ")}')

    @property
    def log_addr(self) -> str:
        """
        日志地址

        :rtype: str
        :return
        """
        if self.connected:
            return f'{self.addr.host}:{self.addr.port}'
        else:
            return 'None:None'

    def looping_call_tasks(self, tasks: List[Callable[[], None]]) -> None:
        """
        执行定时任务

        :rtype: None
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

    def eb_loop_failed(self, failure: Failure) -> None:
        """
        循环任务失败时候调用

        :rtype: None
        :param failure:
        :return:
        """
        pass

    def cb_loop_done(self, result) -> None:
        """
        在循环任务完成时调用

        :rtype: None
        :param result:
        :return:
        """
        pass

    def send(self, data: bytes, log_prefix: str = '') -> None:
        """
        发送数据

        :rtype: None
        :param log_prefix:
        :param data:
        :return:
        """
        if self.connected:
            logger.debug(f'{log_prefix} - Send to {self.log_addr}: {data.hex(" ")}')
            self.transport.write(data)
        else:
            logger.error(f'{log_prefix} - Send failed, self.connected is 0.')
            return


class IotControlTcpClient(_IotControlClientMixin, TcpClient):
    """
    在TcpClient的基础之上，增加了对物联智控的mqtt控制的支持以及相关的工具函数

    """
    pass


class TcpClientFactory(ReconnectingClientFactory):
    """
    基础tcp client的工厂类

    """

    protocol = TcpClient
    # 最大重连时间
    maxDelay = 10
    # 延时因子
    factor = 1.6180339887498948

    def clientConnectionLost(self, connector, unused_reason) -> None:
        addr = connector.getDestination()
        logger.critical(f"Connection is lost {addr.host}:{addr.port}. reason: {unused_reason}")
        return super().clientConnectionLost(connector, unused_reason)

    def clientConnectionFailed(self, connector, reason) -> None:
        addr = connector.getDestination()
        logger.critical(f"Connection is lost {addr.host}:{addr.port}. reason: {reason}")
        return super().clientConnectionLost(connector, reason)

    @classmethod
    def set_protocol(cls, protocol: Callable[[], Protocol], *args, **kwargs) -> 'TcpClientFactory':
        """
        设置protocol参数

        :param protocol:
        :param args:
        :param kwargs:
        :return:
        """
        return cls.forProtocol(protocol, *args, **kwargs)

    @classmethod
    def init(cls) -> None:
        """
        实现初始化动作

        :return:
        """
        logger.info(f'{cls.__name__} init.')


class IotMqttClientFactory(_IotFactoryMixin, TcpClientFactory):
    """
    增加了mqtt_client，使之于mqtt broker保持通信

    """
    mqtt_client = IotMqttClient()
