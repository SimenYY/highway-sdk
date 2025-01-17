#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
e.g. following

from typing import Optional

from highway_sdk.transport.aProtocol import AsyncTcpProtocol, AsyncTcpFactory, connect_tcp
from highway_sdk.transport.aTask import LoopingCallTask
import asyncio

from highway_sdk.core.log import logger
from highway_sdk.core.log.handlers import ColoredStreamHandler

logger.addHandler(ColoredStreamHandler())
logger.setLevel('DEBUG')


class DemoProtocol(AsyncTcpProtocol):
    humanize = True

    def connection_made(self, transport: Optional[asyncio.Transport]) -> None:
        super().connection_made(transport)

        LoopingCallTask(self.task_hello).start(1.0)
        LoopingCallTask(self.task_fuck).start(2.0, soon=True)

    def task_hello(self):
        self.send(b'Hello, world!')

    def task_fuck(self):
        self.send(b'Fuck, world!')

    def data_received(self, data) -> None:
        super().data_received(data)
        self.send(data)


class DemoFactory(AsyncTcpFactory):
    protocol = DemoProtocol


if __name__ == '__main__':
    asyncio.run(connect_tcp('127.0.0.1', 8888, DemoFactory()))
"""
import asyncio
import inspect
import random
from dataclasses import dataclass
from typing import Optional, Callable, Dict, Final

from highway_sdk.core.log import logger


@dataclass
class Address:
    host: str
    port: int

    def __hash__(self):
        return hash((self.host, self.port))

    def __eq__(self, other):
        if isinstance(other, Address):
            return self.host == other.host and self.port == other.port
        return False

    def __str__(self):
        return f"{self.host}:{self.port}"


@dataclass
class DelayState:
    delay: float = 1.0
    retries: int = 0
    continue_trying: bool = True

    def __str__(self):
        return f"delay= {self.delay} seconds,retries= {self.retries} times,continue_trying= {self.continue_trying}"


class AsyncTcpProtocol(asyncio.Protocol):
    default_encoding: Final[str] = 'utf-8'
    default_interval: Final[float] = 1.0
    # polling interval
    interval: float = default_interval

    encoding: str = default_encoding
    factory: Optional['AsyncTcpFactory'] = None

    humanize: bool = False

    def __init__(self):
        self.addr: Optional[Address] = None

        self.transport: Optional[asyncio.Transport] = None

        self.loop = asyncio.get_running_loop()

    def connection_made(self, transport: Optional[asyncio.Transport]) -> None:

        peername = transport.get_extra_info('peername')
        self.addr = Address(host=peername[0], port=peername[1])

        logger.info(f"Connection is established {self.addr}.")

        self.transport = transport

    def send(self, data: bytes, auto_log_caller: bool = True) -> None:
        """

        :param data:
        :param auto_log_caller: 自动打印调用者
        :return:
        """
        _f = "{}Send to {} - {}".format

        if auto_log_caller:
            caller = f'{inspect.stack()[1].function} - '
        else:
            caller = ''

        if self.transport:
            self.transport.write(data)

            logger.debug(_f(caller, self.addr, data.hex(" ")))
            if self.humanize:
                logger.debug(_f(caller, self.addr, data.decode(self.encoding, errors="ignore")))
        else:
            ValueError(f"transport is None")

    def data_received(self, data) -> None:
        _f = "Received from {} - {}".format

        logger.debug(_f(self.addr, data.hex(" ")))
        if self.humanize:
            logger.debug(_f(self.addr, data.decode(self.encoding, errors="ignore")))

    def connection_lost(self, exc) -> None:
        self.transport = None

        if exc is None:
            self.factory.connection_lost(self.addr)
        else:
            self.factory.connection_abort(exc, self.addr)


class AsyncTcpFactory:
    protocol: Optional[Callable[[], AsyncTcpProtocol]] = None

    max_delay: float = 3600.0
    max_retries: Optional[int] = None
    initial_delay: Final[float] = 1.0

    factor: float = 1.6180339887498948
    jitter: float = 0.119626565582

    def __init__(self):
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self.delay_pool: Dict[Address, DelayState] = {}

    def connection_lost(self, addr: Address) -> None:
        logger.error(f"Connection lost {addr}.")
        self.retry(addr)

    def connection_abort(self, exc, addr: Address) -> None:
        logger.critical(f"Connection abort {addr} - {exc}")
        self.retry(addr)

    def reset_delay(self, addr: Address) -> None:
        rm = self.delay_pool.get(addr)

        if rm is None:
            self.delay_pool[addr] = DelayState()
            return

        rm.delay = self.initial_delay
        rm.retries = 0
        rm.continue_trying = True
        logger.debug(f"Reset delay state for {rm}.")

    @classmethod
    def set_protocol(cls, protocol: Callable[[], AsyncTcpProtocol]) -> 'AsyncTcpFactory':
        factory = cls()
        factory.protocol = protocol
        return factory

    def retry(self, addr: Address) -> None:
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

        rm.delay = round(rm.delay, 2)
        logger.debug(f"{addr} will retry in {rm.delay} seconds.")

        if self.loop is None:
            self.loop = asyncio.get_running_loop()

        self.loop.call_later(rm.delay, lambda: asyncio.create_task(self.reconnect(addr)))

    async def reconnect(self, addr: Address):
        try:
            loop = asyncio.get_running_loop()
            await loop.create_connection(
                protocol_factory=lambda: self(addr=addr),
                host=addr.host,
                port=addr.port
            )
        except Exception as e:
            logger.error(f'Connect to {addr} failed - {e}')
            self.retry(addr)

    def __call__(self, addr: Address, *args, **kwargs) -> AsyncTcpProtocol:
        if self.protocol is None:
            raise ValueError("protocol is None.")

        self.reset_delay(addr)
        p = self.protocol()
        p.factory = self
        return p


async def connect_tcp(
        host: str,
        port: int,
        protocol_factory: AsyncTcpFactory,
        loop: Optional[asyncio.AbstractEventLoop] = None
) -> None:
    if loop is None:
        loop = asyncio.get_running_loop()
    else:
        loop = loop

    addr = Address(host=host, port=port)
    protocol = protocol_factory(addr=addr)
    try:
        await loop.create_connection(
            protocol_factory=lambda: protocol,
            host=host,
            port=port
        )
    except Exception as e:
        logger.error(f'Connect to {addr} failed - {e}')
        protocol_factory.retry(addr)
    finally:
        event = asyncio.Event()
        await event.wait()
