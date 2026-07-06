"""传输层模块。

提供 TCP 连接管理，支持自动重连。
"""

import asyncio
import logging
import random

from .exceptions import (
    ConnectionLostError,
    ConnectionTimeoutError,
    DeviceConnectionError,
    ResponseTimeoutError,
)

logger = logging.getLogger(__name__)


class Transport:
    """TCP 传输层。

    提供连接管理、数据收发、自动重连功能。

    ponytail: 一个类解决所有传输问题，不需要 ProtocolTransport 和 ReconnectingTransport。
    """

    def __init__(
        self,
        host: str,
        port: int,
        *,
        timeout: float = 3.0,
        auto_reconnect: bool = False,
        reconnect_interval: float = 1.0,
        max_reconnect_attempts: int = 0,
    ):
        """初始化传输层。

        Args:
            host: 目标主机地址。
            port: 目标端口。
            timeout: 连接超时时间（秒）。
            auto_reconnect: 是否自动重连。
            reconnect_interval: 重连间隔（秒）。
            max_reconnect_attempts: 最大重连次数（0 表示无限重连）。
        """
        self.host = host
        self.port = port
        self.timeout = timeout
        self.auto_reconnect = auto_reconnect
        self.reconnect_interval = reconnect_interval
        self.max_reconnect_attempts = max_reconnect_attempts

        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None
        self._connected = False
        self._reconnect_count = 0
        self._reconnect_task: asyncio.Task | None = None
        # 主动断开标志：区分「主动 disconnect」（不再重连）与「被动断连」（可重连），
        # 避免直接覆写 auto_reconnect 导致用户初始配置丢失。
        self._closing = False

        # 使用标准 logging，通过 extra 传递设备信息
        self.logger = logger
        self._log_prefix = f"[{host}:{port}]"

    @property
    def is_connected(self) -> bool:
        """是否已连接。"""
        return self._connected and self._writer is not None and not self._writer.is_closing()

    def __repr__(self) -> str:
        state = "connected" if self.is_connected else "disconnected"
        return f"Transport(host={self.host!r}, port={self.port}, state={state})"

    async def connect(self) -> None:
        """建立连接。

        Raises:
            ConnectionTimeoutError: 连接超时。
            DeviceConnectionError: 连接失败。
        """
        try:
            self._reader, self._writer = await asyncio.wait_for(
                asyncio.open_connection(self.host, self.port),
                timeout=self.timeout,
            )
            self._connected = True
            self._reconnect_count = 0
            self.logger.info(f"{self._log_prefix} Connected")
        except TimeoutError:
            raise ConnectionTimeoutError(f"Connection timeout after {self.timeout}s") from None
        except OSError as e:
            raise DeviceConnectionError(f"Connection failed: {e}") from e

    async def disconnect(self) -> None:
        """断开连接。

        主动断开后不再触发自动重连，但 ``auto_reconnect`` 初始配置保持不变——
        下次 ``connect()`` 后仍可恢复自动重连行为。
        """
        self._closing = True
        if self._reconnect_task and not self._reconnect_task.done():
            self._reconnect_task.cancel()
            try:
                await self._reconnect_task
            except asyncio.CancelledError:
                pass

        if self._writer:
            self._writer.close()
            await self._writer.wait_closed()
        self._reader = None
        self._writer = None
        self._connected = False
        self._closing = False
        self.logger.info(f"{self._log_prefix} Disconnected")

    async def send(self, data: bytes) -> None:
        """发送数据。

        Args:
            data: 要发送的字节数据。

        Raises:
            ConnectionLostError: 连接已断开。
        """
        if not self.is_connected:
            if self._should_reconnect():
                await self._wait_for_reconnect()
            if not self.is_connected:
                raise ConnectionLostError("Not connected")

        assert self._writer is not None
        self._writer.write(data)
        await self._writer.drain()
        self.logger.debug(f"{self._log_prefix} TXD >> {data.hex(' ')}")

    async def receive(self, bufsize: int = 1024) -> bytes:
        """接收数据。

        Args:
            bufsize: 缓冲区大小。

        Returns:
            bytes: 接收到的数据。

        Raises:
            ConnectionLostError: 连接已断开。
        """
        if not self.is_connected:
            if self._should_reconnect():
                await self._wait_for_reconnect()
            if not self.is_connected:
                raise ConnectionLostError("Not connected")

        assert self._reader is not None
        data = await self._reader.read(bufsize)
        if not data:
            raise ConnectionLostError("Connection closed by peer")

        self.logger.debug(f"{self._log_prefix} RXD << {data.hex(' ')}")
        return data

    async def request(self, data: bytes, timeout: float | None = None) -> bytes:
        """请求-响应模式。

        发送数据并等待响应。

        Args:
            data: 要发送的数据。
            timeout: 响应超时时间（秒）。``None`` 表示使用初始化时的 ``self.timeout``。

        Returns:
            bytes: 接收到的响应数据。

        Raises:
            ConnectionLostError: 连接已断开。
            ResponseTimeoutError: 响应超时。
        """
        if not self.is_connected:
            if self._should_reconnect():
                await self._wait_for_reconnect()
            if not self.is_connected:
                raise ConnectionLostError("Not connected")

        assert self._reader is not None and self._writer is not None

        effective_timeout = self.timeout if timeout is None else timeout

        self._writer.write(data)
        await self._writer.drain()
        self.logger.debug(f"{self._log_prefix} TXD >> {data.hex(' ')}")

        try:
            response = await asyncio.wait_for(self._reader.read(1024), effective_timeout)
            self.logger.debug(f"{self._log_prefix} RXD << {response.hex(' ')}")
            return response
        except TimeoutError:
            raise ResponseTimeoutError(f"Response timeout after {effective_timeout}s") from None

    def _should_reconnect(self) -> bool:
        """是否应该触发自动重连（仅当启用自动重连且非主动断开）。"""
        return self.auto_reconnect and not self._closing

    async def _reconnect_loop(self) -> None:
        """重连循环。"""
        interval = self.reconnect_interval

        while self._should_reconnect():
            try:
                await self.connect()
                self.logger.info(f"{self._log_prefix} Reconnected successfully")
                return
            except Exception as e:
                self._reconnect_count += 1
                self.logger.error(f"{self._log_prefix} Reconnect failed: {e}")

                if self.max_reconnect_attempts > 0 and self._reconnect_count >= self.max_reconnect_attempts:
                    self.logger.error(
                        f"{self._log_prefix} Max reconnect attempts ({self.max_reconnect_attempts}) reached"
                    )
                    # 达到上限：用 _closing 阻止后续重连，保留 auto_reconnect 原值
                    self._closing = True
                    return

                interval = min(interval * 1.618, 60.0)
                if self.reconnect_interval > 0:
                    interval += random.uniform(-0.1 * interval, 0.1 * interval)

                self.logger.info(
                    f"{self._log_prefix} Reconnecting in {interval:.2f}s (attempt {self._reconnect_count})"
                )
                await asyncio.sleep(interval)

    async def _wait_for_reconnect(self) -> None:
        """等待重连完成。"""
        if self._reconnect_task is None or self._reconnect_task.done():
            self._reconnect_task = asyncio.create_task(self._reconnect_loop())

        try:
            await asyncio.wait_for(self._reconnect_task, timeout=self.timeout * 3)
        except TimeoutError:
            self.logger.error(f"{self._log_prefix} Reconnect timeout")

    async def __aenter__(self):
        """异步上下文管理器入口。"""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口。"""
        await self.disconnect()
