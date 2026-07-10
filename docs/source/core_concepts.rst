核心概念
==========

Highway SDK 引入了一些核心概念，理解这些概念将有助于您更好地使用和扩展 SDK。

架构层次
--------

SDK 自上而下分为四层：

1. **Device（设备层）** - 厂商设备客户端，提供数据采集与控制 API
2. **Codec（编解码层）** - 帧 ↔ 数据标签转换，基于装饰器注册解码器
3. **Frame（帧定义层）** - 厂商特定的帧结构与序列化
4. **Transport（传输层）** - 异步 TCP 客户端，内置自动重连

传输层 (Transport)
------------------

**定义**：异步 TCP 客户端，负责字节流传输、连接管理、请求-响应匹配。

**关键能力**：

- 基于 ``asyncio`` 的连接建立、断开、收发
- 内置自动重连（指数退避，可配置最大重试次数）
- 请求-响应模式：``await transport.request(data, timeout=None)``
- 上下文管理器：``async with transport:``

**类**：``highway_sdk.core.transport.Transport``

帧 (Frame)
----------

**定义**：厂商特定的数据帧结构，由 ``start + address + what + data + crc + end`` 组成。

**类层级**：

- ``BaseFrame``（``core/frame.py``）- Pydantic 模型基类，字段 ``what`` 为 ``Any`` 以允许厂商覆盖为枚举
- ``CMSFrame``（``vendors/cms/_base.py``）- CMS 通用帧基类，提供 CRC、转义等共享逻辑
- 厂商 ``Frame``（``vendors/cms/<vendor>/spec.py``）- 实现 ``__bytes__()`` 序列化与 ``from_bytes()`` 解析

编解码器 (Codec)
----------------

**定义**：将响应帧解码为 ``dict``，将业务参数编码为请求帧的 data 域。

**关键约定**：

- 子类通过 ``__init_subclass__`` 隔离 ``decoders`` 注册表，避免跨厂商污染
- 使用 ``@BaseCodec.register(What.XXX)`` 类方法装饰器注册解码器（返回原函数，不包装）
- ``BaseCodec.decode(frame)`` 统一分发到对应 ``decode_xxx(data)`` 方法
- 自 v3.0.0 起 ``decode()`` 返回 ``dict``（不再是 ``BaseTags`` 子类）

设备 (Device)
-------------

**定义**：厂商设备客户端，对外提供数据采集与控制 API，对内封装帧构造与响应解析。

**关键约定**：

- ``BaseDevice[CodecT]`` 是泛型基类（``Generic[CodecT]``，**不继承 ABC**）
- 厂商设备 ``class XVendorDevice(BaseDevice[XVendorCodec])``
- 工厂入口：``await XVendorDevice.connect(host, port)`` 或通过注册表 ``connect_device("vendor", host, port)``
- ``_request`` 方法 ``timeout: float | None = None`` 默认回退 ``Transport`` 初始化超时
- 设备方法采用 **Pythonic 异常模式**：成功返回业务数据（数据采集返回 ``dict`` = ``CmsTags.model_dump(exclude_none=True)``，控制方法返回 ``None``），失败抛 ``HighwaySDKError`` 子类异常（业务失败抛 ``DeviceOperationError``，超时抛 ``ResponseTimeoutError``，连接异常抛 ``DeviceConnectionError``）

数据标签 (Tags)
----------------

**定义**：设备返回数据的标准化结构。

**当前约定**：

- ``BaseTags`` 自 v3.0.0 起 **已弃用于 codec 解码路径**（``decode()`` 返回 ``dict``）
- ``BaseTags`` 仅为公开 API 兼容性保留
- CMS 厂商统一使用 ``CmsTags`` / ``CmsPlayItem``（位于 ``vendors/cms/tags.py``），禁止厂商自定义 Tags 类

厂商注册表 (Vendor Registry)
-----------------------------

**定义**：运行时厂商注册中心，支持配置驱动的动态设备创建。

**核心组件**：

- ``VendorMetadata`` - 冻结 dataclass，含 ``name``、``display_name``、``device_type``、``device_class``、``codec_class``
- ``VendorRegistry`` - 注册表类，管理注册与查询
- ``list_vendors()`` / ``get_vendor(name)`` / ``create_device(vendor, host, port)`` / ``connect_device(vendor, host, port)`` - 工厂函数
- ``register_vendor(metadata)`` - 注册自定义厂商

**自动注册**：``vendors/__init__.py`` 导入各厂商模块时，模块的 ``__init__.py`` 通过 ``register_vendor()`` 自动注册 ``metadata``。

厂商实现 (Vendor Implementation)
---------------------------------

**目录结构**：每个 CMS 厂商实现固定 3 个文件：

- ``spec.py`` - 帧定义（``What`` 枚举、``Frame`` 类、地址/编码常量）
- ``codec.py`` - 编解码器（``XCodec(BaseCodec)``，注册 ``decode_xxx`` 方法）
- ``device.py`` - 设备客户端（``XDevice(BaseDevice[XCodec])``）

**目录禁止**：禁止 ``factory.py`` / ``parser.py`` / ``protocol.py`` / ``media.py`` 等旧架构文件。

异常处理 (Exception)
---------------------

**基类**：``HighwaySDKError``

**关键约定**：

- 连接异常基类用 ``DeviceConnectionError``（**禁止** ``ConnectionError``，避免遮蔽内建 ``OSError`` 子类）
- 帧校验异常基类用 ``FrameValidationError``（**禁止** ``ValidationError``，避免遮蔽 ``pydantic.ValidationError``）

日志 (Logging)
--------------

**核心函数**：``get_logger(name)`` 返回标准 ``logging.Logger`` 实例。

**约定**：库只提供日志接口，不配置日志输出；应用负责配置（``logging.basicConfig`` 或对接 ``loguru``/``structlog``）。

下一步
------

- 阅读 `架构设计 <architecture>`_ 了解 SDK 的设计理念
- 查看 `API 参考 <api_reference/index>`_ 了解详细的 API 文档
- 阅读 `使用指南 <../guide>`_ 学习典型使用场景
