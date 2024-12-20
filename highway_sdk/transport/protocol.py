#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:FileName: protocol.py
:Project:
:Brand:
:Version:
:Description: 
:Author: He YinYu
:Link:
:Time: 2024/12/17 20:20
"""
import random
import inspect

from dataclasses import dataclass
from typing import Dict, Optional, Callable, Type, List, Final

from twisted.internet.interfaces import IAddress
from twisted.internet.protocol import ClientFactory, Protocol
from twisted.internet.task import LoopingCall
from twisted.internet.tcp import Connector
from twisted.python.failure import Failure

from highway_sdk.core.logx import logger
from highway_sdk.transport.strategy import RecvStrategy


@dataclass
class DeviceProperty:
    series: str = None
    sn: str = None


class ClientProtocol(Protocol):
    """
    Handing the data transfer and protocol logic on the network connection.

    The functional points are as follows
    1. scheduled communication.
    2. logs of sending and receiving.
    """
    DEFAULT_ENCODING: Final[str] = 'utf-8'
    DEFAULT_INTERVAL: Final[float] = 5.0

    interval: float = DEFAULT_INTERVAL

    encoding: str = DEFAULT_ENCODING

    humanize: bool = False

    recv_strategy: Optional[RecvStrategy] = None

    factory: Optional['ClusterReconnectClientFactory'] = None

    def connectionMade(self) -> None:
        logger.success(f"Connection is established {self.log_addr}.")

    def dataReceived(self, data: bytes) -> None:
        logger.debug(f'Receive from {self.log_addr} - {self.data_format(data)}')

    def data_format(self, data: bytes) -> str:

        if self.humanize:
            msg = data.decode(self.encoding, 'ignore')
        else:
            msg = data.hex(" ").upper()
        return msg

    @property
    def log_addr(self) -> str:
        if self.transport is None:
            msg = f'[None:None]'
        else:
            addr = self.transport.getPeer()
            msg = f'[{addr.host}:{addr.port}]'
        return msg

    def looping_call_tasks(self, tasks: List[Callable[[], None]]) -> None:

        for task in tasks:
            self.looping_call_task(task)

    def looping_call_task(self, task: Callable[[], None]) -> None:

        if self.interval <= 0:
            self.interval = self.DEFAULT_INTERVAL

        interval = self.interval
        jitter = self.factory.JITTER
        if jitter is not None:
            interval = random.normalvariate(interval,
                                            interval * jitter)
        loop_deferred = LoopingCall(task).start(interval, now=False)
        loop_deferred.addErrback(self.eb_loop_failed)
        loop_deferred.addCallback(self.cb_loop_done)

    @staticmethod
    def eb_loop_failed(failure: Failure) -> None:

        logger.error(f"Looping call failed: {failure}")

    @staticmethod
    def cb_loop_done(result) -> None:

        logger.info(f"Looping call done: {result}")

    def send(self, data: bytes) -> None:

        caller_name = inspect.stack()[1].function
        if self.connected:
            logger.debug(f'{caller_name} - Send to {self.log_addr} - {self.data_format(data)}')
            self.transport.write(data)
        else:
            logger.error(f'{caller_name} - Send failed, self.connected is 0.')


@dataclass
class DelayState:
    delay: float = 1.0
    retries: int = 0
    continue_trying: bool = True


class ClusterReconnectClientFactory(ClientFactory):
    """
    1. Factory which auto-reconnects client with an exponential backoff.
    2. A device corresponds to a delay state.
    3. log optimization.
    """
    protocol: Optional[Callable[[], Protocol]] = None

    max_delay: float = 3600.0
    max_retries: Optional[int] = None
    initial_delay: float = 1.0

    FACTOR: Final[float] = 1.6180339887498948
    JITTER: Final[float] = 0.119626565582

    delay_pool: Dict[IAddress, DelayState] = {}

    clock = None

    def clientConnectionFailed(self, connector: Connector, reason: Failure):
        addr = connector.getDestination()
        logger.error(f"Connection is failed {addr}, reason: {reason}.")
        self.retry(connector)

    def clientConnectionLost(self, connector: Connector, reason: Failure):
        addr = connector.getDestination()
        logger.error(f"Connection is lost {addr}, reason: {reason}.")
        self.retry(connector)

    def buildProtocol(self, addr: IAddress) -> "Optional[Protocol]":
        self.reset_delay(addr)
        p = self.protocol()
        p.factory = self
        return p

    @classmethod
    def set_protocol(cls, protocol: Type[Protocol], *args, **kwargs):
        return cls.forProtocol(protocol, *args, **kwargs)

    def retry(self, connector: Connector) -> None:

        addr = connector.getDestination()
        rm = self.delay_pool.get(addr)

        # Didn't connect in the first place.
        if rm is None:
            rm = DelayState()
            self.delay_pool[addr] = rm

        if not rm.continue_trying:
            logger.warning(f"Abandoning {addr} on explicit request")
            return

        rm.retries += 1
        if self.max_retries is not None and (rm.retries > self.max_retries):
            logger.warning(f"Abandoning {addr} after {rm.retries} retries.")
            return

        rm.delay = min(rm.delay * self.FACTOR, self.max_delay)
        if self.JITTER is not None:
            rm.delay = random.normalvariate(rm.delay, rm.delay * self.JITTER)

        logger.info(f"{addr} will retry in {rm.delay} seconds.")
        self.reconnect_later(rm.delay, connector)

    def reset_delay(self, addr: IAddress) -> None:

        rm = self.delay_pool.get(addr)

        if rm is None:
            self.delay_pool[addr] = DelayState()
            return

        rm.delay = self.initial_delay
        rm.retries = 0
        rm.continue_trying = True

    def reconnect_later(self, delay: float, connector: Connector) -> None:
        if self.clock is None:
            from twisted.internet import reactor
            self.clock = reactor

        self.clock.callLater(delay, connector.connect)
