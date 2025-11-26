from datetime import datetime, timedelta
import logging
import random
import asyncio
from typing import Self
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from highway_sdk.core.log import PrefixLoggerAdapter
from highway_sdk.core.interface import BaseMessageChainParser
from .exceptions import (
    HostResponseTimeoutError,
    ConnectionFailError,
    ConnectionLostError,
)
from .reader import MessageReader

logger = logging.getLogger(__name__)


# ==============================================================================
# asyncio streams client
# ==============================================================================
class AioTCPClient:
    def __init__(
        self,
        host: str,
        port: int,
        *,
        timeout: float = 3.0,
        bufsize: int = 2**10,  # 1KB
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
    def address(self):
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
            logger.info(f"Connected to {self.address}")
        except (asyncio.TimeoutError, ConnectionRefusedError, OSError) as e:
            msg = f"Failed to connect to {self.address} - {e}"
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
        logger.info(f"Disconnected from server {self.address}")

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
# protocol 类
# ==============================================================================
class TCPClientProtocol(asyncio.Protocol):
    """TCP 客户端协议类

    核心功能包括：
        1. 自定义协议开发、
        2. 自动重连机制、
        3. 完善的日志

    Attributes:
        _on_lost_fut (asyncio.Future): 连接丢失的 Future 对象
        _loop (asyncio.AbstractEventLoop): 事件循环
        _transport (asyncio.Transport): 传输对象
        log (PrefixLoggerAdapter): 日志适配器
    """

    def __init__(
        self,
        on_lost_fut: asyncio.Future | None = None,
        loop: asyncio.AbstractEventLoop | None = None,
    ) -> None:
        self._on_lost_fut = on_lost_fut
        self._transport: asyncio.Transport | None = None
        self._loop = loop or asyncio.get_running_loop()
        self.log: PrefixLoggerAdapter = PrefixLoggerAdapter(logger)

    def connection_made(self, transport: asyncio.Transport) -> None:
        """连接建立时回调

        Args:
            transport (asyncio.Transport): 传输对象

        """

        self._transport = transport
        self.log = PrefixLoggerAdapter(
            logger, prefix=str(list(transport.get_extra_info("peername")))
        )
        self.log.info("Connection made")
        self.on_connected()

    def data_received(self, data: bytearray) -> None:
        """数据接收时回调

        Args:
            data (bytes): 接收到的数据
        """
        self.log.debug(f"RXD << {data.hex(' ')}")

        self.on_data_received(data)

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

        on_lost_fut = self._on_lost_fut
        if on_lost_fut is not None and not on_lost_fut.cancelled():
            on_lost_fut.set_result(True)
            self._on_lost_fut = None

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
        if not self.is_connected:
            raise ConnectionError("Connection lost")

        assert self._transport is not None
        self._transport.write(data)
        self.log.debug(f"TXD >> {data.hex(' ')}")

    def on_connected(self) -> None:
        """连接建立后的钩子方法"""
        pass

    def on_data_received(self, data: bytearray) -> None:
        """数据接收时候的钩子方法

        Args:
            data (bytearray): _description_
        """
        pass

    def on_disconnected(self) -> None:
        """连接断开后的钩子方法"""
        pass


class TCPClientDriverProtocol(TCPClientProtocol):
    """适用于驱动的协议

    核心功能包括：
        1. 完善的调度器
        2. 报文读取处理

    Args:
        TCPClientProtocol (_type_): _description_

    Raises:
        ConnectionError: _description_
        ValueError: _description_
        ValueError: _description_
        RuntimeError: _description_
        RuntimeError: _description_
        ValueError: _description_

    Returns:
        _type_: _description_
    """

    parser: BaseMessageChainParser | None = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.scheduler = AsyncIOScheduler()  # 调度器
        self.reader = MessageReader()

    def connection_made(self, transport: asyncio.Transport) -> None:
        if not self.scheduler.running:
            self.scheduler.start()
        return super().connection_made(transport)

    def connection_lost(self, exc: Exception | None) -> None:
        if self.scheduler.running:
            self.scheduler.shutdown()

        return super().connection_lost(exc)

    def data_received(self, data: bytearray) -> None:
        self.log.debug(f"RXD << {data.hex(' ')}")
        self.reader.feed_data(data)
        self.on_data_received(data)

    def add_interval_jobs(self, func_list: list, delay_seconds: float = 2.0):
        """添加间隔任务"""
        gap = delay_seconds / len(func_list)
        if gap < 0.1:
            # TODO: 增加gap过小的异常
            pass
        now = datetime.now()
        for i, func in enumerate(func_list):
            self.scheduler.add_job(
                func,
                "interval",
                seconds=delay_seconds,
                next_run_time=now + timedelta(seconds=gap * i),
            )


class TCPClientSequenceDriverProtocol(TCPClientDriverProtocol):
    """顺序请求响应协议

    基于发送顺序匹配响应的同步机制：
    1. 使用队列维护发送命令的顺序
    2. 使用相同顺序的Future队列等待对应的响应
    3. 按照先进先出(FIFO)原则匹配响应与请求
    4. 实现超时机制保证可靠性

    Args:
        TcpClientProtocol (_type_): _description_
    """

    def __init__(
        self,
        on_lost_fut: asyncio.Future | None = None,
        loop: asyncio.AbstractEventLoop | None = None,
    ) -> None:
        super().__init__(on_lost_fut, loop)

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
                if isinstance(resp, bytearray):
                    return resp
                else:
                    return bytearray(resp)
            except asyncio.TimeoutError:
                self.log.error(f"[REQ] {name}: timeout(>{timeout}s)")
                raise HostResponseTimeoutError("Host response timeout")
            finally:
                if not resp_fut.done():
                    resp_fut.cancel()

    def data_received(self, data: bytearray) -> None:
        """数据接收时回调

        Args:
            data (bytearray): 接收到的数据
        """
        self.log.debug(f"RXD << {data.hex(' ')}")

        if not self._resp_queue.empty():
            resp_future = self._resp_queue.get_nowait()
            if not resp_future.done():
                resp_future.set_result(data)
        self.on_data_received(data)


class TCPConnector:
    """TCP连接类

    Attributes:
        host (str): 服务器地址
        port (int): 服务器端口
        auto_reconnect (bool): 是否自动重连. Defaults to True.
        use_jitter (bool): 是否使用重连抖动. Defaults to False.
        protocol_class (Type[TcpClientProtocol], optional): 协议类. Defaults to TcpClientProtocol.
        _loop (asyncio.AbstractEventLoop): 事件循环
        _retry_delay (float): 重连延迟
        _continue_trying (bool): 是否继续尝试连接
        _on_lost_fut (asyncio.Future): 非正常连接丢失回调Future

    Example:
    >>> connector = TcpConnector.create("127.0.0.1", 8000, protocol_class=YourProtocol)

    """

    min_delay: float = 1.0
    max_delay: float = 60.0

    factor: float = 1.6180339887498948
    jitter: float = 0.119626565582

    def __init__(
        self,
        host: str,
        port: int,
        auto_reconnect: bool,
        use_jitter: bool,
        protocol_class: type[TCPClientProtocol],
        loop: asyncio.AbstractEventLoop | None = None,
    ):
        self.host = host
        self.port = port
        self.auto_reconnect = auto_reconnect
        self.protocol_class = protocol_class
        self.use_jitter = use_jitter

        self._loop = loop or asyncio.get_running_loop()
        self._retry_delay = self.min_delay
        self._continue_trying = True
        self._on_lost_fut = self._loop.create_future()

    @classmethod
    async def create(
        cls,
        host: str,
        port: int,
        *,
        auto_reconnect: bool = True,
        use_jitter: bool = False,
        protocol_class: type[TCPClientProtocol] = TCPClientProtocol,
        loop: asyncio.AbstractEventLoop | None = None,
    ) -> Self:
        """创建连接

        Node:
            如果auto_reconnect为True, 则会阻塞协程

        Args:
            host (str): 服务器地址
            port (int): 服务器端口
            auto_reconnect (bool): 是否自动重连. Defaults to True.
            use_jitter (bool): 是否使用重连抖动. Defaults to False.
            protocol_class (Type[TcpClientProtocol], optional): 协议类. Defaults to TcpClientProtocol.

        Returns:
            Self: 连接实例
        """
        connector = cls(host, port, auto_reconnect, use_jitter, protocol_class, loop)

        if connector.auto_reconnect:
            await connector._reconnect()
        else:
            await connector._connect()

        return connector

    def close(self) -> None:
        """关闭连接"""
        if self.is_connected():
            assert self._transport is not None, "transport is None"
            self._transport.close()
            self._transport = None
            logger.info(f"Disconnected from {self.log_address()}")

    async def _connect(self) -> None:
        """连接"""
        transport, protocol = await self._loop.create_connection(
            lambda: self.protocol_class(self._on_lost_fut, self._loop),
            self.host,
            self.port,
        )
        self._transport = transport
        self._protocol = protocol

    async def _reconnect(self) -> None:
        """重连

        Note:
            实现说明，连接成功后，因为等待`self._on_lost_fut`的结果，当前函数会被暂时搁置，
            当`self._on_lost_fut`结果返回时，当前函数会继续执行，并重新连接。
        """
        while self._continue_trying:
            try:
                await self._connect()
                self._reset_delay()
                on_lost_fut = self._on_lost_fut
                if await on_lost_fut:
                    self.close()
                    self._protocol = None
                    self._on_lost_fut = self._loop.create_future()
                    continue
                else:
                    break
            except OSError as e:
                self._increase_delay()
                logger.info(
                    f"Failed to connect to {self.log_address()}: {e} Reconnecting...(after {self._retry_delay: 0.2f} s)"
                )
            finally:
                # 断开后，一定在延时后再连接，避免二次触发protocol的连接回调
                await asyncio.sleep(self._retry_delay)

    def stop_retry(self) -> None:
        """停止重连"""
        if self._continue_trying:
            self._continue_trying = False

    def _reset_delay(self) -> None:
        """重置重连时延"""
        self._retry_delay = self.min_delay

    def _increase_delay(self) -> None:
        """增加重连时延

        Note:
            时延抖动是根据正态分布计算
        """
        self._retry_delay = min(self._retry_delay * self.factor, self.max_delay)
        if self.use_jitter:
            self._retry_delay = random.normalvariate(
                self._retry_delay, self.jitter * self._retry_delay
            )

    def is_connected(self) -> bool:
        return self._transport is not None and not self._transport.is_closing()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(host={self.host}, port={self.port})"

    def log_address(self) -> str:
        return f"{self.host}:{self.port}"
