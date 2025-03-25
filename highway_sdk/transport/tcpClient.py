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
from typing import Type, List, Callable, Optional, Dict
import redis

from twisted.internet.address import IPv4Address
from twisted.internet.interfaces import IAddress
from twisted.internet.protocol import Protocol, ReconnectingClientFactory, connectionDone
from twisted.internet.task import LoopingCall
from twisted.python import failure
from twisted.python.failure import Failure

from highway_sdk.core.log import logger
from .strategy import RecvStrategy
from ..core.client import Client
from ..interface.iot import IotMqttClient
from highway_sdk.interface.database.redisClient import RedisClient

__all__ = [
    "TcpClient",
    "IotTcpClient",
    "TcpClientFactory",

    "IotControlTcpClient",
    "IotMqttClientFactory",

    "RedisClientFactory",
    "RedisTcpClient",
]


class _IotControlClientMixin:
    """
    物联智控控制混入
    """

    def iot_subscribe(self, on_message: Callable[..., None]):
        if not hasattr(self.factory, 'mqtt_client'):
            logger.error("mqtt_client not found in %s", self.factory.__name__)
            return

        if self.factory.mqtt_client is None:
            logger.error("%s mqtt_client is None.", self.factory.__name__)
            return

        self.factory.mqtt_client.subscribe_control_req(
            series=self.series,
            sn=self.sn,
            on_message=on_message
        )


class _IotClientMixin:
    """
    物联智控mqtt客户端混入
    """
    factory: Optional['IotMqttClientFactory'] = None

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
            logger.error('get_topic_host failed, %s', e)
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
        logger.info('接受到控制指令 - topic=%s, payload=%s', message.topic, message.payload)

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
            logger.error('%s - Send failed, %s.', log_prefix, e)


class TcpClient(Protocol):
    """
    用于基于TCP协议的设备的客户端，具备与设备通信交互的功能
    """
    # 默认轮询时间
    DEFAULT_INTERVAL = 5
    # 轮询时间
    polling_interval = DEFAULT_INTERVAL
    # 随机抖动因子
    jitter = 0.119626565582
    # 数据接受策略
    recv_strategy: Type[RecvStrategy] = None
    # 设备产品型号
    series: Optional[str] = None
    # 报文编码
    encoding: str = 'utf-8'

    factory: Optional['TcpClientFactory'] = None

    def __init__(self):
        self.addr: Optional[IPv4Address] = None
        self.lc_list: List[LoopingCall] = []

    @property
    def sn(self) -> str:
        return f'{self.series}_{self.addr.host}'

    def makeConnection(self, transport):
        self.factory.preprocess()

        return super().makeConnection(transport)

    def connectionMade(self) -> None:
        self.addr = self.transport.getPeer()
        logger.info("Connection is established %s.", self.log_addr)

    def dataReceived(self, data: bytes) -> None:
        logger.debug('Receive from %s - %s', self.log_addr, data.hex(" "))

    @property
    def log_addr(self) -> str:
        """日志地址

        :rtype: str
        :return
        """
        if self.connected:
            return f'{self.addr.host}:{self.addr.port}'
        else:
            return 'None:None'

    def looping_call_tasks(self, tasks: List[Callable[[], None]], now: bool = False) -> None:
        """执行定时任务

        :param tasks:
        :param now:
        :return:
        """

        for task in tasks:
            self.looping_call_task(task, now=now)

    def looping_call_task(self, task: Callable[[], None], now: bool = False) -> None:
        # 验证轮询时间的合法性，否则设置为默认值
        if self.polling_interval <= 0:
            self.polling_interval = self.DEFAULT_INTERVAL

        interval = self.polling_interval
        if self.jitter:
            interval = random.normalvariate(self.polling_interval,
                                            self.polling_interval * self.jitter)

        lc = LoopingCall(task)
        self.lc_list.append(lc)
        ld = lc.start(interval, now=now)
        ld.addErrback(self.eb_loop_failed)
        ld.addCallback(self.cb_loop_done)

    def connectionLost(self, reason: failure.Failure = connectionDone) -> None:
        self.stop_looping_call()

    def stop_looping_call(self) -> None:
        """
        连接断开再连接，会叠加任务调用，因此断开时需要主动停止
        :return:
        """
        if len(self.lc_list) == 0:
            return

        for lc in self.lc_list:
            lc.stop()
        self.lc_list.clear()

    def eb_loop_failed(self, _failure: Failure) -> None:
        logger.error("Host(%s)'s looping call failed: %s", self.log_addr, _failure)

    def cb_loop_done(self, result) -> None:

        logger.info("Host(%s)'s looping call done: %s", self.log_addr, result)

    def send(self, data: bytes, log_prefix: Optional[str] = None) -> None:
        """
        发送数据

        :rtype: None
        :param log_prefix:
        :param data:
        :return:
        """
        if self.connected:
            logger.debug('%s - Send to %s - %s', log_prefix, self.log_addr, data.hex(" "))
            self.transport.write(data)
        else:
            logger.error('%s - Send failed, self.connected is 0.', log_prefix)
            return


class TcpClientFactory(ReconnectingClientFactory):
    """
    基础tcp client的工厂类
    """

    protocol = TcpClient
    # 延时因子
    factor = 1.6180339887498948
    # 用于维护活动的客户端
    clients: Dict[IPv4Address, TcpClient] = {}

    @property
    def current_clients_count(self) -> int:
        return len(self.clients)

    def before_reconnect(self, connector, reason) -> None:
        """
        在重连之前处理

        :param reason:
        :param connector:
        :return:
        """
        addr = connector.getDestination()
        removed = self.remove_client(addr)
        condition = 'Lost' if removed else 'Failed'
        logger.critical("Connection is %s %s:%s. reason: %s", condition, addr.host, addr.port, reason)

    def remove_client(self, addr: IAddress) -> bool:
        """
        :param addr:
        :return: 是否删除
        """
        removed = False
        if addr in self.clients:
            del self.clients[addr]
            removed = True
        return removed

    @classmethod
    def set_protocol(cls, protocol: Callable[[], Protocol], *args, **kwargs) -> 'TcpClientFactory':
        """设置protocol参数

        :param protocol:
        :param args:
        :param kwargs:
        :return:
        """
        return cls.forProtocol(protocol, *args, **kwargs)

    def buildProtocol(self, addr: IAddress) -> "Optional[Protocol]":
        self.resetDelay()
        p = self.protocol()
        p.factory = self
        self.clients[addr] = p
        return p

    def clientConnectionLost(self, connector, unused_reason) -> None:
        self.before_reconnect(connector, unused_reason)
        return super().clientConnectionLost(connector, unused_reason)

    def clientConnectionFailed(self, connector, reason) -> None:
        self.before_reconnect(connector, reason)
        return super().clientConnectionLost(connector, reason)

    def preprocess(self):
        """预处理
        一般放在make_connection中

        :return:
        """
        pass


"""**************************************************
                    Mqtt
**************************************************"""


class IotTcpClient(_IotClientMixin, TcpClient):
    """
    上层平台为物联智控的设备客户端
    """
    pass


class IotControlTcpClient(_IotControlClientMixin, TcpClient):
    """
    在TcpClient的基础之上，增加了对物联智控的mqtt控制的支持以及相关的工具函数
    """
    pass


class IotMqttClientFactory(TcpClientFactory):
    """
    增加了mqtt_client，使之于mqtt broker保持通信
    """
    mqtt_client: IotMqttClient = IotMqttClient()

    def preprocess(self):
        self.mqtt_client.connect()


"""**************************************************
                    Redis
**************************************************"""


class RedisClientFactory(TcpClientFactory):
    """
    发送设备数据要redis
    """
    redis_client = RedisClient()

    def preprocess(self):
        self.redis_client.noblock_start()


class _RedisClientMixin:
    """
    redis客户端混入
    """
    factory: Optional['RedisClientFactory'] = None


class RedisTcpClient(_RedisClientMixin, TcpClient):
    """
    数据发送到redis的设备客户端
    """
    pass
