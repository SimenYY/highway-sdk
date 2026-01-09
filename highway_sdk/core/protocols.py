from collections.abc import Callable
from datetime import datetime, timedelta
import logging
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from highway_sdk.core.log import PrefixLoggerAdapter
from highway_sdk.core.base import BaseMessageParser
from .exceptions import (
    HostResponseTimeoutError,
    ConnectionFailError,
    ConnectionLostError,
)
from .reader import Reader
from .constants import BUFSIZE

logger = logging.getLogger(__name__)


# ==============================================================================
# asyncio streams client
# ==============================================================================
class AioTCPClient:
    """asyncio client"""

    def __init__(
        self,
        host: str,
        port: int,
        *,
        timeout: float = 3.0,
        bufsize: int = BUFSIZE,  # 1KB
        loop: asyncio.AbstractEventLoop | None = None,
    ):
        self._host = host
        self._port = port
        self._timeout = timeout
        self._loop = loop or asyncio.get_running_loop()
        self._lock = asyncio.Lock()
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None
        self._connected: bool = False
        self._bufsize: int = bufsize

    @property
    def host_addr(self):
        return f"{self._host}:{self._port}"

    @property
    def is_connected(self) -> bool:
        return (
            self._connected
            and self._writer is not None
            and self._reader is not None
            and not self._writer.is_closing()
        )

    async def connect(self):
        """建立连接"""
        if self._connected:
            return

        try:
            self._reader, self._writer = await asyncio.wait_for(
                asyncio.open_connection(self._host, self._port), timeout=self._timeout
            )
            self._connected = True
            logger.info(f"Connected to {self.host_addr}")
        except (asyncio.TimeoutError, ConnectionRefusedError, OSError) as e:
            msg = f"Failed to connect to {self.host_addr} - {e}"
            logger.error(msg)
            raise ConnectionFailError("connection fail") from e

    async def disconnect(self):
        """断开连接"""
        if not self._connected:
            return

        if self._writer:
            self._writer.close()
            await self._writer.wait_closed()
        self._reader = None
        self._writer = None
        self._connected = False
        logger.info(f"Disconnected from server {self.host_addr}")

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()

    async def request(self, msg: bytes, timeout: float = 3.0) -> bytes:
        """请求-响应

        Args:
            msg (bytes): _description_
            timeout (float): _description_
        Raises:
            HostResponseTimeoutError: _description_
            ConnectionFailureError: _description_

        Returns:
            _type_: _description_
        """

        if not self.is_connected:
            raise ConnectionLostError("connection lost")

        assert self._writer is not None and self._reader is not None

        async with self._lock:
            self._writer.write(msg)
            await self._writer.drain()
            try:
                return await asyncio.wait_for(self._reader.read(self._bufsize), timeout)
            except asyncio.TimeoutError:
                raise HostResponseTimeoutError("Host response timeout")


# ==============================================================================
# Protocol 类：封装通信交互行为
# ==============================================================================
class UDPProtocol(asyncio.DatagramProtocol):
    """UDP 协议"""

    def __init__(
        self,
        on_con_lost: asyncio.Future,
        loop: asyncio.AbstractEventLoop | None = None,
    ) -> None:
        self._on_con_lost = on_con_lost
        self._loop = loop or asyncio.get_running_loop()

    def connection_lost(self, exc: Exception | None) -> None:
        self._on_con_lost.set_result(True)


class TCPClientProtocol(asyncio.Protocol):
    """TCP 客户端协议"""

    def __init__(
        self,
        on_con_lost: asyncio.Future,
        loop: asyncio.AbstractEventLoop | None = None,
    ) -> None:
        self._on_con_lost = on_con_lost
        self._loop = loop or asyncio.get_running_loop()
        self._transport: asyncio.Transport | None = None
        self.reader = Reader()
        self.log: PrefixLoggerAdapter = PrefixLoggerAdapter(logger)

    @property
    def host_addr(self):
        if self._transport is None:
            raise RuntimeError("Transport not initialized")
        return self._transport.get_extra_info("peername")

    def connection_made(self, transport: asyncio.Transport) -> None:
        """连接建立时回调

        Args:
            transport (asyncio.Transport): 传输对象

        """
        self._transport = transport
        self.log = PrefixLoggerAdapter(logger, prefix=str(list(self.host_addr)))
        self.log.info("Connection made")
        self.on_connected()

    def data_received(self, data: bytes) -> None:
        """数据接收时回调

        Args:
            data (bytes): 接收到的数据
        """
        self.log.debug(f"RXD << {data.hex(' ')}")
        self.reader.feed_data(data)
        self.on_data_fed()

    def connection_lost(self, exc: Exception | None) -> None:
        """连接丢失时回调

        exc为None的三种情况：
            1. 主动断开，例如transport.close()，
            2. 对端关闭端口，
            3。对端主动断开客户端

        Args:
            exc (Exception | None): 如果时None，则表示主动断开，例如transport.close()，否则含有异常信息
        """

        self.log.error(f"Connection lost: {exc}")

        on_con_fut = self._on_con_lost
        if on_con_fut is not None and not on_con_fut.cancelled():
            on_con_fut.set_result(True)
            self._on_con_lost = None

        self._transport = None
        self.on_disconnected()

    @property
    def is_connected(self) -> bool:
        """判断是否连接

        Returns:
            bool: 连接状态
        """
        return self._transport is not None and not self._transport.is_closing()

    def send(self, data: bytes) -> None:
        """发送数据

        Args:
            data (bytes): 需要发送的数据

        Raises:
            ConnectionError: transpost 不存在或者正在关闭
        """
        if self._transport is None or self._transport.is_closing():
            raise ConnectionError("Connection lost")

        self._transport.write(data)
        self.log.debug(f"TXD >> {data.hex(' ')}")

    def on_connected(self) -> None:
        """连接建立后的钩子方法"""
        pass

    def on_data_fed(self) -> None:
        """数据接收时候的钩子方法"""
        pass

    def on_disconnected(self) -> None:
        """连接断开后的钩子方法"""
        pass


class DriverTCPClientProtocol(TCPClientProtocol):
    """TCP 客户端驱动协议

    Args:
        TCPClientProtocol (_type_): _description_

    Notes:
        AsyncIOScheduler是可以动态的增添任务的

    Returns:
        _type_: _description_
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.scheduler = AsyncIOScheduler()  # 调度器

    def add_interval_job(
        self, func: Callable[[], None], seconds: float, jitter: int = 1
    ):
        """添加间隔任务， 有随机抖动"""
        self.scheduler.add_job(func, "interval", seconds=seconds, jitter=jitter)

    def connection_made(self, transport: asyncio.Transport) -> None:
        if not self.scheduler.running:
            self.scheduler.start()
        return super().connection_made(transport)

    def connection_lost(self, exc: Exception | None) -> None:
        if self.scheduler.running:
            self.scheduler.shutdown()
        return super().connection_lost(exc)


class ReqRespTCPClientProtocol(DriverTCPClientProtocol):
    """请求响应协议"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._resp_queue = asyncio.Queue()  # 等待响应队列
        self._lock = asyncio.Lock()

    async def request(
        self, name: str, payload: bytes, timeout: float = 2.0
    ) -> bytearray:
        """请求并等待响应

        Args:
            name (str): 请求名
            payload (bytes): 请求负载
            timeout (float, optional): 请求超时时间. Defaults to 2.0.

        Raises:
            ConnectionError: _description_

        Returns:
            bytearray: _description_
        """
        if not self.is_connected:
            raise ConnectionError("Transport can't be used")

        async with self._lock:
            resp_fut = self._loop.create_future()
            await self._resp_queue.put(resp_fut)

            try:
                self.send(payload)

                resp = await asyncio.wait_for(
                    resp_fut, timeout
                )  # 超时自动取消传入的Future
                return bytearray(resp)
            except asyncio.TimeoutError:
                self.log.error(f"[REQ] {name}: timeout(>{timeout}s)")
                raise HostResponseTimeoutError("Host response timeout")
            finally:
                if not resp_fut.done():
                    resp_fut.cancel()

    def data_received(self, data: bytes) -> None:
        """数据接收时回调"""

        self.log.debug(f"RXD << {data.hex(' ')}")

        if not self._resp_queue.empty():
            resp_future = self._resp_queue.get_nowait()
            if not resp_future.done():
                resp_future.set_result(data)
        self.on_data_fed()
