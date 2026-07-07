# Highway SDK

Highway SDK 是一个用于高速公路机电设备通信的 Python 异步库，提供统一的设备协议接入抽象。

## 功能特性

- **统一接口**：一致的 API 接口，屏蔽不同厂商协议差异
- **多厂商支持**：集成多个 CMS 厂商的协议实现
- **异步优先**：基于 asyncio 的高性能异步 I/O
- **自动重连**：内置指数退避重连机制
- **类型提示**：完整的 Python 类型提示
- **模块化设计**：易于扩展新厂商支持

## 支持的设备与厂商

### CMS (可变信息标志)

- [x] 电明 (DianMing)
- [x] 丰海 (FengHai)
- [x] 诺瓦 (Nova)
- [x] 三思 (SanSi)
- [x] 显科 (XianKe)

### VD (车检器)

- [ ] 待添加

## 安装

```bash
# 从 PyPI 安装
pip install highway-sdk

# 从源码安装
git clone https://github.com/your-organization/highway-sdk.git
cd highway-sdk
poetry install
```

## 快速开始

### 基础使用

```python
import asyncio
from highway_sdk import DianMingDevice

async def main():
    # 连接设备并获取信息
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
from highway_sdk import Transport, FengHaiDevice

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
    device = FengHaiDevice(transport)

    try:
        brightness = await device.get_brightness()
        print(f"亮度: {brightness}")
    finally:
        await device.disconnect()
```

### 多厂商设备管理

```python
from highway_sdk import (
    DianMingDevice, FengHaiDevice, NovaDevice,
    SanSiDevice, XianKeDevice
)

async def main():
    # 设备配置
    devices_config = [
        (DianMingDevice, "192.168.1.100", 9000),
        (FengHaiDevice, "192.168.1.101", 9000),
        (NovaDevice, "192.168.1.102", 9000),
    ]

    # 批量连接
    devices = []
    for device_class, host, port in devices_config:
        device = await device_class.connect(host, port)
        devices.append(device)

    # 批量操作
    for device in devices:
        brightness = await device.get_brightness()
        print(f"{device.__class__.__name__}: {brightness}")

    # 断开连接
    for device in devices:
        await device.disconnect()
```

### 厂商注册表（物联网平台集成）

```python
from highway_sdk import list_vendors, get_vendor, connect_device

# 查看所有已注册厂商
for vendor in list_vendors():
    print(f"{vendor.name}: {vendor.display_name} ({vendor.device_type})")

# 通过厂商名动态创建设备（适合配置驱动场景）
device = await connect_device("dianming", "192.168.1.100", 9000)
brightness = await device.get_brightness()
```

## 核心架构

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
| Tags      | 设备返回数据标准化（v3.0.0 起已弃用于 codec 路径） | `BaseTags`   |

## 开发新厂商协议

### 1. 定义帧结构

```python
# highway_sdk/vendors/cms/myvendor/spec.py
from enum import IntEnum
from highway_sdk.vendors.cms._base import CMSFrame

class What(IntEnum):
    GET_BRIGHTNESS = 0x01
    SET_BRIGHTNESS = 0x02

class Frame(CMSFrame):
    def __bytes__(self) -> bytes:
        return self.start + bytes([self.what]) + self.data + self.end
```

### 2. 实现编解码器

```python
# highway_sdk/vendors/cms/myvendor/codec.py
from highway_sdk.core.codec import BaseCodec

class MyCodec(BaseCodec):
    @classmethod
    @BaseCodec.register(What.GET_BRIGHTNESS)
    def decode_brightness(cls, data: bytes) -> dict:
        return {"value": data[0], "mode": data[1]}
```

### 3. 实现设备类

```python
# highway_sdk/vendors/cms/myvendor/device.py
from datetime import datetime

from highway_sdk.core.device import BaseDevice
from highway_sdk.core.exceptions import DeviceOperationError
from highway_sdk.vendors.cms.tags import CmsTags
from .codec import MyCodec
from .spec import Frame, What

class MyDevice(BaseDevice):
    """厂商设备客户端。

    所有方法成功返回业务数据（dict）或 None，失败抛 ``DeviceOperationError`` 等
    ``HighwaySDKError`` 子类异常，由调用方捕获处理。
    """

    codec = MyCodec

    async def _request(self, frame: Frame, timeout: float | None = None) -> Frame:
        response = await self.request(frame, timeout)
        return Frame.from_bytes(response)

    async def get_brightness(self) -> dict:
        """获取亮度信息。

        Raises:
            DeviceOperationError: 设备返回错误响应。
        """
        frame = Frame(what=What.GET_BRIGHTNESS)
        response = await self._request(frame)
        data = self.codec.decode(response)
        cms_tags = CmsTags(
            brightness=data["value"],
            brightness_mode="auto" if data["mode"] == 0 else "manual",
            timestamp=datetime.now(),
        )
        return cms_tags.model_dump()
```

## 日志使用

```python
from highway_sdk import get_logger

# 获取日志实例（开箱即用，默认输出到控制台）
logger = get_logger("my_app")
logger.info("应用启动")

# 配置日志文件输出
logger = get_logger(
    "my_app",
    level="DEBUG",
    log_dir="./logs",
    rotation="00:00",
    retention="3 days",
    compression="zip"
)
```

## 异常处理

Highway SDK 采用 Pythonic 异常模式：**成功返回业务数据（`dict` 或 `None`），失败抛 ``HighwaySDKError`` 子类异常**。调用方按业务场景捕获对应异常即可，无需逐次检查响应状态。

```python
from highway_sdk.core.exceptions import (
    ConnectionTimeoutError,
    ConnectionLostError,
    ResponseTimeoutError,
    DeviceOperationError,
)

try:
    async with await DianMingDevice.connect("192.168.1.100", 9000) as device:
        # 数据采集返回 dict，失败抛 DeviceOperationError
        data = await device.get_brightness()
        print(f"亮度: {data['brightness']}%")
        # 控制方法成功返回 None，失败抛 DeviceOperationError
        await device.set_brightness(brightness=20)
except ConnectionTimeoutError:
    print("连接超时")
except ConnectionLostError:
    print("连接断开")
except ResponseTimeoutError:
    print("响应超时")
except DeviceOperationError as e:
    # 业务失败：设备返回错误响应、协议版本不匹配、数据损坏等
    print(f"操作失败: {e}")
```

## 项目结构

```
highway-sdk/
├── highway_sdk/              # 主源码目录
│   ├── core/                 # 核心模块
│   │   ├── transport.py      # 传输层
│   │   ├── codec.py          # 编解码器基类
│   │   ├── device.py         # 设备基类
│   │   ├── frame.py          # 帧基类
│   │   ├── tags.py           # 数据标签基类
│   │   └── exceptions.py     # 异常定义
│   ├── vendors/              # 厂商实现
│   │   └── cms/              # CMS 设备
│   │       ├── dianming/     # 电明
│   │       ├── fenghai/      # 丰海
│   │       ├── nova/         # 诺瓦
│   │       ├── sansi/        # 三思
│   │       └── xianke/       # 显科
│   └── utils/                # 工具函数
├── tests/                    # 测试目录
├── examples/                 # 示例代码
└── docs/                     # 文档
```

## 开发指南

### 运行测试

```bash
# 运行所有测试
poetry run pytest tests/ -v

# 运行特定测试
poetry run pytest tests/test_transport.py -v
```

### 代码检查

```bash
# 运行 pre-commit 检查
pre-commit run --all-files
```

## 许可证

GNU GPL v3 - 详见 [LICENSE](LICENSE.txt)

## 联系方式

- 维护者：Adz Lovelace
- 邮箱：heyinyu.sensi@foxmail.com
