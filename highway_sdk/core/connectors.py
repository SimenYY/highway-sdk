from collections.abc import Callable
import logging
import random
import asyncio
from .protocols import TCPClientProtocol, UDPProtocol

logger = logging.getLogger(__name__)

# ==============================================================================
# Connector 类：封装连接行为
# ==============================================================================
class BaseConnector:
    """连接器基类"""

    def __init__(
        self,
        host: str,
        port: int,
        protocol_factory: Callable[..., TCPClientProtocol | UDPProtocol],
        loop: asyncio.AbstractEventLoop | None = None,
    ) -> None:
        self.host = host
        self.port = port
        self.protocol_cls = protocol_factory
        self._loop = loop or asyncio.get_running_loop()
        self._transport: asyncio.BaseTransport | None = None
        self._protocol: asyncio.BaseProtocol | None = None
        self._on_con_lost = self._loop.create_future()  # 连接丢失future

    @property
    def protocol(self):
        return self._protocol

    @property
    def transport(self):
        return self._transport

    async def create(self):
        """创建连接器，生成transpost、protocol

        Returns:
            _type_: _description_
        """

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.host}, {self.port})"


class UDPConnector(BaseConnector):
    """UDP 连接器

    Args:
        BaseConnector (_type_): _description_

    Returns:
        _type_: _description_
    """

    def __init__(
        self,
        host: str,
        port: int,
        protocol_cls: type[UDPProtocol],
        *,
        local_addr: tuple[str, int] | None = None,
        loop: asyncio.AbstractEventLoop | None = None,
    ) -> None:
        super().__init__(host, port, protocol_cls, loop)
        self.local_addr = local_addr

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}[remote_addr=({self.host},{self.port}), local_addr={self.local_addr}]"

    async def create(self):
        self._transport, self._protocol = await self._loop.create_datagram_endpoint(
            lambda: self.protocol_cls(self._on_con_lost, self._loop),
            local_addr=self.local_addr,
            remote_addr=(self.host, self.port),
        )


class TCPConnector(BaseConnector):
    """TCP 连接器

    Args:
        BaseConnector (_type_): _description_

    Returns:
        _type_: _description_
    """

    def __init__(
        self,
        host: str,
        port: int,
        protocol_cls: type[TCPClientProtocol],
        loop: asyncio.AbstractEventLoop | None = None,
    ) -> None:
        super().__init__(host, port, protocol_cls, loop)

    async def create(self) -> None:
        self._transport, self._protocol = await self._loop.create_connection(
            lambda: self.protocol_cls(on_con_lost=self._on_con_lost, loop=self._loop),
            host=self.host,
            port=self.port,
        )
        if await self._on_con_lost:
            self.close()

    @property
    def is_connected(self) -> bool:
        return self._transport is not None and not self._transport.is_closing()

    def close(self) -> None:
        """关闭连接"""
        if self.is_connected:
            assert self._transport is not None, "transport is None"
            self._transport.close()
            self._transport = None
            self._protocol = None
            logger.info(f"Disconnected from {self}")


class TCPReconnectingConnector(TCPConnector):
    """TCP 重新连接的连接类

    Args:
        TCPConnector (_type_): _description_

    Returns:
        _type_: _description_
    """

    min_delay: float = 1.0
    max_delay: float = 60.0

    factor: float = 1.6180339887498948
    jitter: float = 0.119626565582

    def __init__(
        self,
        host: str,
        port: int,
        protocol_cls: type[TCPClientProtocol],
        *,
        auto_reconnect: bool = True,
        use_jitter: bool = False,
        loop: asyncio.AbstractEventLoop | None = None,
    ) -> None:
        super().__init__(host, port, protocol_cls, loop)

        self.auto_reconnect = auto_reconnect
        self.use_jitter = use_jitter
        self._retry_delay = self.min_delay
        self._continue_trying = True

    async def create(self):
        if self.auto_reconnect:
            await self._reconnect()
        else:
            await self._connect()

    async def _connect(self) -> None:
        """连接"""
        self._transport, self._protocol = await self._loop.create_connection(
            lambda: self.protocol_cls(on_con_lost=self._on_con_lost, loop=self._loop),
            self.host,
            self.port,
        )

    async def _reconnect(self) -> None:
        """重连

        Note:
            实现说明，连接成功后，因为等待`self._on_con_lost`的结果，当前函数会被暂时搁置，
            当`self._on_con_lost`结果返回时，当前函数会继续执行，并重新连接。
        """
        while self._continue_trying:
            try:
                await self._connect()
                self._reset_delay()
                on_lost_fut = self._on_con_lost
                if await on_lost_fut:
                    self.close()
                    self._protocol = None
                    self._on_con_lost = self._loop.create_future()
                    continue
                else:
                    break
            except OSError as e:
                self._increase_delay()
                logger.error(
                    f"Failed to connect to {self}: {e} Reconnecting...(after {self._retry_delay: 0.2f} s)"
                )
            finally:
                # 断开后，在延时后再连接，避免二次触发protocol的连接回调
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
