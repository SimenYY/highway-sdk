.. Highway SDK 文档

Highway SDK 文档
================

Highway SDK 是一个用于管理和控制高速公路常用机电设备和智能设备的统一接口库，支持多个厂商的协议实现。

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

.. toctree::
   :maxdepth: 2
   :caption: 使用示例

   usage_examples/index

.. toctree::
   :maxdepth: 2
   :caption: 集成指南

   platform_integrations/index
   broker_integrations/index

.. toctree::
   :maxdepth: 1
   :caption: 开发指南

   contributing
   changelog


功能特性
--------

- **统一接口**：提供一致的 API 接口，屏蔽不同厂商协议的差异
- **多厂商支持**：集成多个 VMS 厂商的 SDK 实现
- **模块化设计**：采用模块化架构，易于扩展新厂商支持
- **完整的协议实现**：支持设备的配置、监控、媒体管理等功能
- **类型提示**：提供完整的 Python 类型提示，提升开发体验
- **代码质量**：使用 Ruff 进行代码检查和格式化，确保代码质量
- **监控支持**：集成 Prometheus 监控，方便设备状态监控

支持的设备与厂商
----------------

### VMS (可变信息标志)
- [x] 丰海 (Fenghai)
- [x] Nova
- [x] Xianke
- [x] Sansi

### VD (车检器)
- [ ] 待添加

> **注**：支持的设备种类和厂商还在持续更新中，欢迎贡献。