平台集成API
============

Highway SDK提供了与各种外部平台的集成功能，便于将设备数据上传到外部平台或从外部平台接收命令。

平台集成概述
------------

平台集成模块提供了与外部平台的通信能力，支持多种平台协议和格式。

**主要功能**：

- 设备数据上传
- 命令接收和处理
- 设备状态同步
- 配置同步

Supaiot平台集成
----------------

Supaiot是一个物联网平台，Highway SDK提供了与Supaiot平台的集成功能。

**核心类**：

.. autoclass:: highway_sdk.platforms.supaiot.client.SupaiotClient
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: highway_sdk.platforms.supaiot.config.SupaiotConfig
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: highway_sdk.platforms.supaiot.protocols.SupaiotProtocol
   :members:
   :undoc-members:
   :show-inheritance:

**使用示例**：

.. code-block:: python

    from highway_sdk.platforms.supaiot.client import SupaiotClient
    from highway_sdk.platforms.supaiot.config import SupaiotConfig

    # 创建Supaiot配置
    config = SupaiotConfig(
        host="supaiot.example.com",
        port=8883,
        client_id="highway-sdk-test",
        username="test",
        password="test"
    )

    # 创建Supaiot客户端
    client = SupaiotClient(config)

    # 连接到平台
    client.connect()

    # 上传设备数据
    client.upload_device_data("device1", {"temperature": 25, "humidity": 60})

    # 接收命令
    def on_command_received(device_id, command):
        print(f"收到设备 {device_id} 的命令: {command}")
        # 处理命令

    client.set_command_callback(on_command_received)

    # 断开连接
    # client.disconnect()

Center平台集成
---------------

Center是一个中心管理平台，Highway SDK提供了与Center平台的集成功能。

**核心类**：

.. autoclass:: highway_sdk.platforms.center.models.CenterDevice
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: highway_sdk.platforms.center.spec.CenterSpec
   :members:
   :undoc-members:
   :show-inheritance:

扩展新平台集成
----------------

要扩展新的平台集成，需要：

1. 在 `highway_sdk/platforms/` 目录下创建新的平台目录
2. 实现平台客户端、配置和协议类
3. 提供设备数据上传和命令接收功能
4. 编写测试用例
5. 更新文档

如果您有兴趣贡献新的平台集成，欢迎提交PR或联系项目维护者。