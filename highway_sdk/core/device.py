"""设备基类模块。

定义了设备客户端的统一接口，提供标准化的设备操作方式。
"""

from collections.abc import Callable
from typing import Any, Generic, Self, TypeVar

from .codec import BaseCodec
from .frame import BaseFrame
from .transport import Transport

CodecT = TypeVar("CodecT", bound=BaseCodec)


class BaseDevice(Generic[CodecT]):
    """设备基类。

    所有设备客户端都应该继承此类，实现统一的设备操作接口。

    子类应通过类变量 ``codec`` 指定厂商编解码器类型，并通过泛型参数声明具体类型：

    Example:
        >>> class MyDevice(BaseDevice[MyCodec]):
        ...     codec = MyCodec
        ...
        ...     async def get_item(self) -> dict:
        ...         response = await self.transport.request(b"...")
        ...         return self.codec.decode(response)
    """

    codec: type[CodecT]

    def __init__(self, transport: Transport):
        """初始化设备。

        Args:
            transport: 传输层实例。
        """
        self.transport = transport

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.transport!r})"

    @classmethod
    async def connect(
        cls,
        host: str,
        port: int,
        *,
        transport_factory: Callable[[str, int], Transport] | None = None,
        **kwargs: Any,
    ) -> Self:
        """连接到设备。

        Args:
            host: 设备地址。
            port: 设备端口。
            transport_factory: 传输层工厂函数，默认使用 Transport。
            ``**kwargs``: 传递给 Transport 的参数。

        Returns:
            BaseDevice: 设备实例。
        """
        factory = transport_factory or Transport
        transport = factory(host, port, **kwargs)
        await transport.connect()
        return cls(transport)

    async def disconnect(self) -> None:
        """断开连接。"""
        await self.transport.disconnect()

    async def send(self, frame: BaseFrame) -> None:
        """发送帧。

        Args:
            frame: 要发送的帧。
        """
        await self.transport.send(bytes(frame))

    async def request(self, frame: BaseFrame, timeout: float | None = None) -> bytes:
        """发送帧并等待响应。

        Args:
            frame: 要发送的帧。
            timeout: 响应超时时间（秒）。``None`` 表示使用 Transport 初始化时的超时。

        Returns:
            bytes: 响应数据。
        """
        return await self.transport.request(bytes(frame), timeout)

    async def __aenter__(self):
        """异步上下文管理器入口。"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口。"""
        await self.disconnect()
