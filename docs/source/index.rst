.. Highway SDK 文档

Highway SDK 文档
================

Highway SDK 是一个用于高速公路机电设备通信的 Python 异步库，提供统一的设备协议接入抽象。

.. toctree::
   :maxdepth: 2
   :caption: 入门指南

   installation
   getting_started

.. toctree::
   :maxdepth: 2
   :caption: 核心概念

   core_concepts
   architecture

.. toctree::
   :maxdepth: 2
   :caption: API参考

   api_reference/index

.. toctree::
   :maxdepth: 2
   :caption: 设备类型

   device_types/index

.. toctree::
   :maxdepth: 2
   :caption: 厂商实现

   vendor_implementations/index

功能特性
--------

- **统一接口**：提供一致的 API 接口，屏蔽不同厂商协议的差异
- **多厂商支持**：集成多个 VMS 厂商的协议实现
- **异步优先**：基于 asyncio 的高性能异步 I/O
- **自动重连**：内置指数退避重连机制
- **类型提示**：完整的 Python 类型提示
- **模块化设计**：易于扩展新厂商支持
- **开箱即用**：日志模块提供零配置默认行为

支持的设备与厂商
----------------

### VMS (可变信息标志)
- [x] 电明 (DianMing)
- [x] 丰海 (FengHai)
- [x] 诺瓦 (Nova)
- [x] 三思 (SanSi)
- [x] 显科 (XianKe)

### VD (车检器)
- [ ] 待添加

> **注**：支持的设备种类和厂商还在持续更新中，欢迎贡献。
