# Highway SDK 使用指南

## 概述

Highway SDK 是一个用于高速公路机电设备通信的 Python 异步库，提供统一的设备协议接入抽象。

## 核心概念

### 架构层次

```
┌─────────────────────────────────────────┐
│           Device (设备层)                │
│  DianMingDevice, FengHaiDevice, ...     │
├─────────────────────────────────────────┤
│           Codec (编解码层)               │
│  DianMingCodec, FengHaiCodec, ...       │
├─────────────────────────────────────────┤
│           Frame (帧定义层)               │
│  Frame, What, ResultCode                │
├─────────────────────────────────────────┤
│           Transport (传输层)             │
│  TCP连接、自动重连、请求-响应            │
└─────────────────────────────────────────┘
```

### 核心组件

| 组件      | 职责                 | 基类         |
| --------- | -------------------- | ------------ |
| Transport | 字节流传输、连接管理 | `Transport`  |
| Frame     | 帧数据结构定义       | `BaseFrame`  |
| Codec     | 帧 ↔ 数据标签转换    | `BaseCodec`  |
| Device    | 设备操作接口         | `BaseDevice` |
| Tags      | 设备返回数据标准化   | `BaseTags`   |

## 快速开始

### 基础使用

```python
import asyncio
from highway_sdk import DianMingDevice

async def main():
    # 连接设备
    async with await DianMingDevice.connect("192.168.1.100", 9000) as device:
        # 获取亮度
        brightness = await device.get_brightness()
        print(f"亮度: {brightness}")

        # 获取播放项
        play_item = await device.get_play_item()
        print(f"当前播放: {play_item}")

asyncio.run(main())
```

### 自定义传输层

```python
from highway_sdk import Transport, DianMingDevice

async def main():
    # 创建带自动重连的传输层
    transport = Transport(
        "192.168.1.100",
        9000,
        auto_reconnect=True,
        reconnect_interval=5.0,
        max_reconnect_attempts=3,
    )

    await transport.connect()
    device = DianMingDevice(transport)

    try:
        brightness = await device.get_brightness()
        print(f"亮度: {brightness}")
    finally:
        await device.disconnect()
```

## 开发新厂商协议

### 1. 定义帧结构

```python
# highway_sdk/vendors/vms/myvendor/spec.py
from enum import IntEnum
from highway_sdk.vendors.vms._base import VMSFrame

class What(IntEnum):
    """指令码定义。"""
    GET_BRIGHTNESS = 0x01
    SET_BRIGHTNESS = 0x02
    GET_PLAY_ITEM = 0x10

class Frame(VMSFrame):
    """厂商帧定义。"""

    def __bytes__(self) -> bytes:
        # 实现帧序列化
        return self.start + bytes([self.what]) + self.data + self.end
```

### 2. 实现编解码器

```python
# highway_sdk/vendors/vms/myvendor/codec.py
from highway_sdk.core.codec import BaseCodec
from highway_sdk.core.tags import BaseTags

class BrightnessTags(BaseTags):
    """亮度数据标签。"""
    value: int
    mode: int

class MyCodec(BaseCodec):
    """厂商编解码器。"""

    @staticmethod
    def decode_brightness(data: bytes) -> BrightnessTags:
        return BrightnessTags(value=data[0], mode=data[1])

# 注册解码函数
MyCodec._decoders[What.GET_BRIGHTNESS] = MyCodec.decode_brightness
```

### 3. 实现设备类

```python
# highway_sdk/vendors/vms/myvendor/device.py
from highway_sdk.core.device import BaseDevice
from highway_sdk.core.tags import BaseTags
from .codec import MyCodec
from .spec import Frame, What

class MyDevice(BaseDevice):
    """厂商设备客户端。"""

    codec = MyCodec

    async def get_brightness(self) -> BaseTags:
        """获取亮度信息。"""
        frame = Frame(what=What.GET_BRIGHTNESS)
        response = await self.request(frame)
        return self.codec.decode(Frame(what=What.GET_BRIGHTNESS, data=response))
```

## API 参考

### Transport

```python
class Transport:
    def __init__(
        self,
        host: str,
        port: int,
        *,
        timeout: float = 3.0,
        auto_reconnect: bool = False,
        reconnect_interval: float = 1.0,
        max_reconnect_attempts: int = 0,
    )

    async def connect(self) -> None
    async def disconnect(self) -> None
    async def send(self, data: bytes) -> None
    async def receive(self, bufsize: int = 1024) -> bytes
    async def request(self, data: bytes, timeout: float = 3.0) -> bytes

    @property
    def is_connected(self) -> bool
```

### BaseDevice

```python
class BaseDevice(ABC):
    codec: type[BaseCodec]
    transport: Transport

    def __init__(self, transport: Transport)

    @classmethod
    async def connect(
        cls,
        host: str,
        port: int,
        *,
        transport_factory: Callable[[str, int], Transport] | None = None,
        **kwargs,
    ) -> "BaseDevice"

    async def disconnect(self) -> None
    async def send(self, frame: BaseFrame) -> None
    async def request(self, frame: BaseFrame, timeout: float = 3.0) -> bytes
```

### BaseCodec

```python
class BaseCodec:
    @classmethod
    def decode(cls, frame: BaseFrame) -> BaseTags

    @classmethod
    def register(cls, what: Any) -> Callable
```

## 厂商注册表

SDK 内置厂商注册表，支持通过厂商标识符动态创建设备实例，适用于物联网平台等配置驱动场景。

### 查看已注册厂商

```python
from highway_sdk import list_vendors

for vendor in list_vendors():
    print(f"{vendor.name}: {vendor.display_name} ({vendor.device_type})")
```

### 动态创建设备

```python
from highway_sdk import connect_device, create_device

# 创建并连接设备
device = await connect_device("dianming", "192.168.1.100", 9000)
brightness = await device.get_brightness()

# 仅创建实例（不连接）
device = create_device("fenghai", "192.168.1.101", 9000)
```

### 注册自定义厂商

```python
from highway_sdk import VendorMetadata, register_vendor

metadata = VendorMetadata(
    name="my_vendor",
    display_name="我的厂商",
    device_type="vms",
    description="自定义厂商协议实现",
    device_class=MyDevice,
    codec_class=MyCodec,
)
register_vendor(metadata)
```

## 支持的厂商

| 厂商 | 标识符     | 设备类           | 编解码器        |
| ---- | ---------- | ---------------- | --------------- |
| 电明 | `dianming` | `DianMingDevice` | `DianMingCodec` |
| 丰海 | `fenghai`  | `FengHaiDevice`  | `FengHaiCodec`  |
| 诺瓦 | `nova`     | `NovaDevice`     | `NovaCodec`     |
| 三思 | `sansi`    | `SanSiDevice`    | `SanSiCodec`    |
| 显科 | `xianke`   | `XianKeDevice`   | `XianKeCodec`   |

## 日志使用

Highway SDK 使用 Python 标准 `logging` 模块作为日志接口。库只提供日志接口，不配置日志输出；应用负责配置日志（如输出到控制台、文件等）。

```python
import logging

# 配置应用日志（应用负责）
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s"
)

# 从 SDK 获取 logger（仅返回 logging.Logger 实例）
from highway_sdk import get_logger

logger = get_logger("highway_sdk.transport")
logger.info("应用启动")
```

应用可自由选择日志后端：标准 `logging`、`loguru`、`structlog` 等，通过 `logging` 的 handler/adapter 机制或拦截器对接即可。

### get_logger 参数

| 参数 | 类型 | 默认值 | 说明                       |
| ---- | ---- | ------ | -------------------------- |
| name | str  | -      | 日志名称，用于标识日志来源 |

## 异常处理

```python
from highway_sdk.core.exceptions import (
    HighwaySDKError,        # 基础异常
    ConnectionError,        # 连接失败
    ConnectionTimeoutError, # 连接超时
    ConnectionLostError,    # 连接断开
    ResponseTimeoutError,   # 响应超时
    ProtocolError,          # 协议错误
)

async def safe_connect():
    try:
        async with await DianMingDevice.connect("192.168.1.100", 9000) as device:
            await device.get_brightness()
    except ConnectionTimeoutError:
        print("连接超时")
    except ConnectionLostError:
        print("连接断开")
    except ResponseTimeoutError:
        print("响应超时")
```

## 测试

```bash
# 运行所有测试
poetry run pytest tests/ -v

# 运行特定测试
poetry run pytest tests/test_transport.py -v
```
