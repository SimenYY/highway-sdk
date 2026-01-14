架构设计
==========

Highway SDK 采用模块化的架构设计，具有良好的扩展性和可维护性。本文档将详细介绍 SDK 的架构设计和模块划分。

整体架构
----------

Highway SDK 的整体架构分为以下几个层次：

1. **核心层 (Core)** - 提供SDK的核心功能
2. **厂商实现层 (Vendors)** - 提供各厂商设备的协议实现
3. **平台集成层 (Platforms)** - 提供与外部平台的集成
4. **消息Broker层 (Brokers)** - 提供消息的发布和订阅功能
5. **工具层 (Utils)** - 提供通用的工具函数

核心层 (Core)
--------------

核心层是SDK的基础，提供了SDK的核心功能，包括：

.. image:: /_static/architecture_core.png
   :alt: 核心层架构

**核心模块**：

1. **base** - 基础类和工具，包括BaseTags等
2. **config** - 配置管理，包括LogConfig等
3. **connectors** - 网络连接器，包括TCPReconnectingConnector和UDPConnector等
4. **exceptions** - 异常定义，包括HighwaySDKException等
5. **log** - 日志配置，包括LoguruConfig等
6. **metrics** - Prometheus监控，包括MetricsMixin和start_prometheus_server等
7. **protocols** - 通信协议，包括DriverTCPClientProtocol和ReqRespTCPClientProtocol等
8. **reader** - 数据读取工具，包括Reader等
9. **settings** - 系统设置，包括各种配置项

厂商实现层 (Vendors)
----------------------

厂商实现层提供了各厂商设备的协议实现，采用模块化设计，便于扩展新的厂商支持。

.. image:: /_static/architecture_vendors.png
   :alt: 厂商实现层架构

**设备类型**：

- **VMS (可变信息标志)** - 提供VMS设备的协议实现
- **VD (车检器)** - 提供VD设备的协议实现

**厂商实现结构**：

对于每个厂商的设备实现，包含以下文件：

- **factory.py** - 帧工厂实现，用于创建设备通信的请求帧
- **parser.py** - 解析器实现，用于解析设备返回的数据
- **protocol.py** - 协议实现，用于处理设备的通信
- **spec.py** - 协议规范定义，包括指令码、帧结构等
- **media.py** - 媒体管理实现，用于处理设备的媒体文件

平台集成层 (Platforms)
------------------------

平台集成层提供了与外部平台的集成，实现设备数据的上传和管理。

**主要平台**：

- **Supaiot** - 苏派物联网平台集成

消息Broker层 (Brokers)
------------------------

消息Broker层提供了消息的发布和订阅功能，支持多种消息协议。

**支持的Broker**：

- **MQTT** - MQTT消息Broker
- **Kafka** - Kafka消息Broker
- **Redis** - Redis消息Broker

工具层 (Utils)
----------------

工具层提供了通用的工具函数，用于简化开发。

**主要工具**：

- **decorator** - 装饰器工具
- **judge** - 判断工具函数
- **lock** - 文件锁工具

数据流图
----------

设备通信的数据流图如下：

.. image:: /_static/dataflow.png
   :alt: 数据流图

1. **应用层** - 应用程序调用SDK的API
2. **SDK核心层** - 处理API请求，创建连接器和协议实例
3. **网络层** - 通过网络发送请求和接收响应
4. **设备层** - 设备处理请求并返回响应
5. **SDK核心层** - 解析设备响应，生成结构化数据
6. **应用层** - 应用程序处理结构化数据

扩展设计
----------

SDK采用了良好的扩展设计，便于扩展新的厂商支持和功能。

**扩展厂商实现**：

1. 在 `highway_sdk/vendors/<device_type>/` 目录下创建新的厂商目录
2. 实现必要的文件：factory.py, parser.py, protocol.py, spec.py, media.py
3. 在 `highway_sdk/vendors/<device_type>/__init__.py` 中导出新的厂商实现

**扩展核心功能**：

1. 在 `highway_sdk/core/` 目录下创建新的模块
2. 实现新的功能
3. 在 `highway_sdk/core/__init__.py` 中导出新的功能

**扩展平台集成**：

1. 在 `highway_sdk/platforms/` 目录下创建新的平台目录
2. 实现平台集成的相关功能
3. 在 `highway_sdk/platforms/__init__.py` 中导出新的平台集成

**扩展消息Broker**：

1. 在 `highway_sdk/brokers/` 目录下创建新的Broker文件
2. 实现Broker的相关功能
3. 在 `highway_sdk/brokers/__init__.py` 中导出新的Broker

设计原则
----------

1. **模块化设计** - 采用模块化架构，便于扩展和维护
2. **统一接口** - 提供一致的API接口，屏蔽不同厂商协议的差异
3. **类型安全** - 提供完整的类型提示，提升开发体验
4. **易于扩展** - 采用面向对象的设计，便于扩展新的厂商支持
5. **可测试性** - 设计易于测试的代码结构，便于编写单元测试
6. **高性能** - 采用异步编程，提高系统的性能和并发能力
7. **可监控** - 集成Prometheus监控，便于系统的监控和调试
8. **良好的文档** - 提供详细的文档，便于用户使用和扩展

下一步
------

- 查看 `API 参考 <api_reference/index>`_ 了解详细的API文档
- 探索 `使用示例 <usage_examples/index>`_ 学习更多使用场景
- 了解 `厂商实现 <vendor_implementations/index>`_ 支持的设备