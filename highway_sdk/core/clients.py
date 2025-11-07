import logging
import asyncio
from typing import ClassVar, Optional, Self
from .exceptions import HostResponseTimeoutError, HostResponseIncompleteError

logger = logging.getLogger(__name__)


class TCPClient:
    """tcp客户端

    首选采用异步的方式进行通信，但是也封装了同步的方法

    同步方法是采用维护一个同步事件循环来进行同步的阻塞操作。

    请求-响应模式采用串行化，即通过asyncio.Lock()进行同步控制。
    """

    _sync_loop: ClassVar[Optional[asyncio.AbstractEventLoop]] = None

    def __init__(
        self, host: str, port: int, *, buffer_size: int = 2**16, timeout: float = 10.0
    ):
        self.host = host
        self.port = port
        self.timeout = timeout
        self._reader: Optional[asyncio.StreamReader] = None
        self._writer: Optional[asyncio.StreamWriter] = None
        self._connected = False
        self._bufsize = buffer_size
        self._lock = asyncio.Lock()

    @property
    def peername(self):
        return f"{self.host}:{self.port}"

    @classmethod
    def connect(cls, host: str, port: int, *, timeout: float = 10.0) -> Self:
        """同步方式创建并连接客户端"""
        if cls._sync_loop is None:
            cls._sync_loop = asyncio.new_event_loop()

        c = cls(host, port, timeout=timeout)
        try:
            cls._sync_loop.run_until_complete(c.aconnect())
            return c
        except Exception:
            cls._sync_loop.close()
            cls._sync_loop = None
            raise

    def disconnect(self):
        if self._sync_loop is None:
            raise RuntimeError("Use sync_connect() to initialize sync client")
        return self._sync_loop.run_until_complete(self.adisconnect())

    async def aconnect(self):
        """异步连接到服务器"""
        if self._connected:
            return

        async with self._lock:
            if self._connected:
                return

            try:
                self._reader, self._writer = await asyncio.wait_for(
                    asyncio.open_connection(self.host, self.port), timeout=self.timeout
                )
                self._connected = True
                logger.info(f"✅Connected to {self.peername}")
            except (asyncio.TimeoutError, ConnectionRefusedError, OSError) as e:
                logger.error(f"❌Failed to connect to {self.peername} - {e}")
                raise

    async def adisconnect(self):
        """断开连接"""
        if not self._connected:
            return

        async with self._lock:
            if self._writer:
                self._writer.close()
                try:
                    await asyncio.wait_for(
                        self._writer.wait_closed(), timeout=self.timeout
                    )
                except asyncio.TimeoutError:
                    pass
            self._reader = None
            self._writer = None
            self._connected = False
            logger.info(f"Disconnected from server {self.peername}")

    async def __aenter__(self):
        await self.aconnect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.adisconnect()

    @property
    def is_connected(self) -> bool:
        return (
            self._connected
            and self._writer is not None
            and not self._writer.is_closing()
        )

    async def asend(self, data: bytes):
        """发送数据

        Args:
            data (bytes): _description_

        Raises:
            ConnectionError: _description_
        """
        async with self._lock:
            if not self.is_connected:
                raise ConnectionError(f"Not connected to {self.peername}")

            assert self._writer is not None
            try:
                self._writer.write(data)
                await self._writer.drain()
            except ConnectionError as e:
                self._connected = False
                raise ConnectionError(
                    f"Failed to send data to {self.peername}: {e}"
                ) from e

    async def arecv(self, n: int = 0, *, is_exactly: bool = False):
        """接收数据

        如果 n > 0 and is_exactly: 精确接收 n 个字节

        如果 n > 0 and not is_exactly: 尽可能多的接收 n 个字节

        如果 n == 0: 使用默认buffer_size, 不等待EOF

        如果 n < 0: 使用默认，会等待EOF

        Args:
            n (int, optional): _description_. Defaults to -1.
            is_exactly (bool, optional): _description_. Defaults to False.

        Raises:
            ConnectionError: _description_

        Returns:
            _type_: _description_
        """
        async with self._lock:
            if not self.is_connected or self._reader is None:
                raise ConnectionError(f"Not connected to {self.peername}")

            try:
                if n > 0 and is_exactly:
                    return await asyncio.wait_for(
                        self._reader.readexactly(n), timeout=self.timeout
                    )
                elif n > 0 and not is_exactly:
                    return await asyncio.wait_for(
                        self._reader.read(n), timeout=self.timeout
                    )
                elif n == 0:  # 使用默认buffer_size
                    return await asyncio.wait_for(
                        self._reader.read(self._bufsize), timeout=self.timeout
                    )
                else:  # n < 0
                    return await asyncio.wait_for(
                        self._reader.read(n), timeout=self.timeout
                    )
            except asyncio.IncompleteReadError as e:
                raise HostResponseIncompleteError(
                    f"Host response incomplete from {self.peername}"
                ) from e
            except asyncio.TimeoutError as e:
                raise HostResponseTimeoutError(
                    f"No data received from {self.peername}"
                ) from e
            except ConnectionError as e:
                self._connected = False
                raise ConnectionError(
                    f"Failed to recv data from {self.peername}: {e}"
                ) from e

    async def arequest(self, data: bytes):
        """响应长度

        ⚠️注意，这个函数接受响应是根据串行化逻辑接受，毕竟简单粗暴，遇到有
        心跳指令的情况不能准确接受对于响应，需要根据协议重写。

        Args:
            data (bytes): _description_
            res_len (int, optional): _description_. Defaults to 64K.

        Returns:
            _type_: _description_
        """
        await self.asend(data)
        return await self.arecv()

    def request(self, data: bytes) -> bytes:
        if self._sync_loop is None:
            raise RuntimeError("Use sync_connect() to initialize sync client")
        return self._sync_loop.run_until_complete(self.arequest(data))

    def send(self, data: bytes):
        """同步发送数据

        Args:
            data (bytes): _description_

        Raises:
            RuntimeError: _description_
        """
        if self._sync_loop is None:
            raise RuntimeError("Use sync_connect() to initialize sync client")

        return self._sync_loop.run_until_complete(self.asend(data))

    def recv(self, n: int = -1):
        """同步接收数据

        Args:
            n (int, optional): _description_. Defaults to -1.

        Raises:
            RuntimeError: _description_

        Returns:
            _type_: _description_
        """
        if self._sync_loop is None:
            raise RuntimeError("Use sync_connect() to initialize sync client")
        return self._sync_loop.run_until_complete(self.arecv(n))
