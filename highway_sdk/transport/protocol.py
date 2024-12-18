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
from dataclasses import dataclass
from typing import Dict, Optional, Callable

from highway_sdk.core.logx import logger
from twisted.internet.interfaces import IAddress
from twisted.internet.protocol import ClientFactory, Protocol
from twisted.internet.tcp import Connector
from twisted.python.failure import Failure


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
    max_delay: float = 3600.0
    max_retries: Optional[int] = None
    initial_delay: float = 1.0

    factor: float = 1.6180339887498948
    jitter: float = 0.119626565582

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
    def set_protocol(cls, protocol: Callable[[], Protocol], *args, **kwargs):
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

        rm.delay = min(rm.delay * self.factor, self.max_delay)
        if self.jitter is not None:
            rm.delay = random.normalvariate(rm.delay, rm.delay * self.jitter)

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
