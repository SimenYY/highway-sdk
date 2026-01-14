消息Broker API
==============

Highway SDK提供了与各种消息Broker的集成功能，便于实现设备数据的发布和订阅。

消息Broker概述
--------------

消息Broker是一种中间件，用于在应用程序之间传递消息，支持发布/订阅模式。

**主要功能**：

- 设备数据的发布和订阅
- 消息路由和转发
- 消息持久化
- 高可用性和可靠性

MQTT Broker集成
----------------

MQTT是一种轻量级的消息传输协议，广泛应用于物联网领域。

**核心类**：

.. autoclass:: highway_sdk.brokers.mqtt.MQTTBroker
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: highway_sdk.brokers.config.MQTTConfig
   :members:
   :undoc-members:
   :show-inheritance:

**使用示例**：

.. code-block:: python

    from highway_sdk.brokers.mqtt import MQTTBroker
    from highway_sdk.brokers.config import MQTTConfig

    # 创建MQTT配置
    config = MQTTConfig(
        host="mqtt.example.com",
        port=1883,
        client_id="highway-sdk-test",
        username="test",
        password="test"
    )

    # 创建MQTT Broker
    broker = MQTTBroker(config)

    # 连接到Broker
    broker.connect()

    # 订阅主题
    def on_message_received(topic, message):
        print(f"收到主题 {topic} 的消息: {message}")
        # 处理消息

    broker.subscribe("highway/devices/#", on_message_received)

    # 发布消息
    broker.publish("highway/devices/device1/data", {"temperature": 25, "humidity": 60})

    # 断开连接
    # broker.disconnect()

Kafka Broker集成
----------------

Kafka是一种高性能的分布式流处理平台，支持大规模消息处理。

**核心类**：

.. autoclass:: highway_sdk.brokers.kafka.KafkaBroker
   :members:
   :undoc-members:
   :show-inheritance:

**使用示例**：

.. code-block:: python

    from highway_sdk.brokers.kafka import KafkaBroker

    # 创建Kafka配置
    config = {
        "bootstrap.servers": "kafka.example.com:9092",
        "group.id": "highway-sdk-test"
    }

    # 创建Kafka Broker
    broker = KafkaBroker(config)

    # 连接到Broker
    broker.connect()

    # 订阅主题
    def on_message_received(topic, message):
        print(f"收到主题 {topic} 的消息: {message}")
        # 处理消息

    broker.subscribe(["highway-devices"], on_message_received)

    # 发布消息
    broker.publish("highway-devices", {"device_id": "device1", "temperature": 25})

    # 断开连接
    # broker.disconnect()

Redis Broker集成
----------------

Redis是一种高性能的键值存储，支持发布/订阅模式。

**核心类**：

.. autoclass:: highway_sdk.brokers.redis.RedisBroker
   :members:
   :undoc-members:
   :show-inheritance:

**使用示例**：

.. code-block:: python

    from highway_sdk.brokers.redis import RedisBroker

    # 创建Redis配置
    config = {
        "host": "redis.example.com",
        "port": 6379,
        "db": 0
    }

    # 创建Redis Broker
    broker = RedisBroker(config)

    # 连接到Broker
    broker.connect()

    # 订阅频道
    def on_message_received(channel, message):
        print(f"收到频道 {channel} 的消息: {message}")
        # 处理消息

    broker.subscribe(["highway-devices"], on_message_received)

    # 发布消息
    broker.publish("highway-devices", {"device_id": "device1", "temperature": 25})

    # 断开连接
    # broker.disconnect()

扩展新Broker集成
----------------

要扩展新的Broker集成，需要：

1. 在 `highway_sdk/brokers/` 目录下创建新的Broker文件
2. 实现Broker客户端类，提供连接、发布、订阅功能
3. 支持配置管理
4. 编写测试用例
5. 更新文档

如果您有兴趣贡献新的Broker集成，欢迎提交PR或联系项目维护者。