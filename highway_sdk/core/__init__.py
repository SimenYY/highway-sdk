"""Highway SDK 核心模块。

提供设备协议接入的基础抽象，包括：
- 传输层：TCP 连接管理
- 协议层：帧解析、命令构建
- 设备层：统一设备接口
"""

from .codec import BaseCodec
from .device import BaseDevice
from .exceptions import (
    ConnectionError,
    ConnectionLostError,
    ConnectionTimeoutError,
    HighwaySDKError,
    ProtocolError,
    ResponseTimeoutError,
)
from .frame import BaseFrame
from .log import LogConfig, setup_logger
from .tags import BaseTags
from .transport import Transport

__all__ = [
    "BaseCodec",
    "BaseDevice",
    "BaseFrame",
    "BaseTags",
    "ConnectionError",
    "ConnectionLostError",
    "ConnectionTimeoutError",
    "HighwaySDKError",
    "LogConfig",
    "ProtocolError",
    "ResponseTimeoutError",
    "Transport",
    "setup_logger",
]
