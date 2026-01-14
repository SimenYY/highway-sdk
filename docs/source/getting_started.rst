快速开始
==========

本指南将帮助您快速上手 Highway SDK，展示如何使用 SDK 连接设备、发送命令和处理响应。

基本使用流程
-------------

1. **配置日志** - 设置 SDK 的日志输出
2. **创建协议类** - 定义设备通信协议
3. **创建连接器** - 建立与设备的连接
4. **发送命令** - 向设备发送请求
5. **处理响应** - 处理设备返回的数据
6. **关闭连接** - 断开与设备的连接

示例代码
--------

下面是一个基本的使用示例：

.. code-block:: python

    import asyncio
    from highway_sdk.core.protocols import DriverTCPClientProtocol
    from highway_sdk.core.connectors import TCPReconnectingConnector
    from highway_sdk.core.log import LoguruConfig

    # 1. 配置日志
    LoguruConfig.intercept_logging(["*"])
    log_config = LoguruConfig(name="vms-sdk", level="INFO")
    log_config.set_console()

    # 2. 创建自定义协议类
    class MyProtocol(DriverTCPClientProtocol):
        """自定义协议类，用于处理设备响应"""
        def on_message_parsed(self, tags):
            """处理解析后的设备响应"""
            print(f"收到设备响应: {tags}")

    async def main():
        # 3. 创建TCP连接器
        connector = TCPReconnectingConnector(
            host="192.168.1.100",
            port=8888,
            protocol_cls=MyProtocol
        )
        
        # 4. 创建连接
        await connector.create()
        
        # 5. 发送命令（根据实际协议类调整）
        if hasattr(connector.protocol, 'get_play_item'):
            connector.protocol.get_play_item()
        
        # 6. 等待一段时间，处理响应
        await asyncio.sleep(5)
        
        # 7. 关闭连接
        connector.close()

    if __name__ == "__main__":
        asyncio.run(main())

多设备管理示例
---------------

下面是一个管理多个设备的示例：

.. code-block:: python

    import asyncio
    from highway_sdk.core.protocols import DriverTCPClientProtocol
    from highway_sdk.core.connectors import TCPReconnectingConnector
    from highway_sdk.core.log import LoguruConfig
    from highway_sdk.core.metrics import start_prometheus_server

    # 1. 配置日志（支持JSON格式）
    LoguruConfig.intercept_logging(["*"])
    log_config = LoguruConfig(name="vms-sdk", level="INFO", serialize=True)
    log_config.set_console()
    log_config.set_file(log_dir="logs")

    # 2. 创建自定义协议类
    class MyProtocol(DriverTCPClientProtocol):
        """自定义协议类，用于处理设备响应"""
        def on_message_parsed(self, tags):
            """处理解析后的设备响应"""
            print(f"收到设备响应: {tags}")

    async def main():
        # 3. 启动Prometheus监控服务器
        prometheus_task = asyncio.create_task(start_prometheus_server(port=8000))
        
        # 4. 创建多个设备连接器
        connectors = []
        devices = [
            {"host": "192.168.1.100", "port": 8888},
            {"host": "192.168.1.101", "port": 8888},
            {"host": "192.168.1.102", "port": 8888}
        ]
        
        for device in devices:
            connector = TCPReconnectingConnector(
                host=device["host"],
                port=device["port"],
                protocol_cls=MyProtocol,
                need_metrics=True  # 启用Prometheus监控
            )
            connectors.append(connector)
        
        # 5. 使用TaskGroup管理多个连接任务
        async with asyncio.TaskGroup() as tg:
            # 创建所有连接
            for connector in connectors:
                tg.create_task(connector.create())
            
            # 等待连接建立
            await asyncio.sleep(2)
            
            # 向所有设备发送命令
            for connector in connectors:
                if hasattr(connector.protocol, 'get_play_item'):
                    connector.protocol.get_play_item()
            
            # 运行一段时间，监控设备
            await asyncio.sleep(30)
        
        # 6. 关闭所有连接
        for connector in connectors:
            connector.close()
        
        # 取消Prometheus服务器任务
        prometheus_task.cancel()
        await prometheus_task

    if __name__ == "__main__":
        asyncio.run(main())

厂商特定协议示例
----------------

下面是一个使用丰海厂商特定协议的示例：

.. code-block:: python

    import asyncio
    from highway_sdk.vendors.vms.fenghai.protocol import VmsFenghaiProtocol
    from highway_sdk.core.connectors import TCPReconnectingConnector
    from highway_sdk.core.log import LoguruConfig

    # 1. 配置日志
    LoguruConfig.intercept_logging(["*"])
    log_config = LoguruConfig(name="fenghai-vms", level="DEBUG")
    log_config.set_console()

    # 2. 使用厂商特定协议
    class MyFenghaiProtocol(VmsFenghaiProtocol):
        """丰海VMS协议处理类"""
        def on_message_parsed(self, tags):
            """处理丰海设备响应"""
            print(f"丰海设备响应: {tags}")

    async def main():
        # 3. 创建连接器
        connector = TCPReconnectingConnector(
            host="192.168.1.100",
            port=8888,
            protocol_cls=MyFenghaiProtocol
        )
        
        # 4. 建立连接
        await connector.create()
        
        # 5. 发送丰海特定命令
        connector.protocol.get_play_item()
        connector.protocol.get_brightness_and_mode()
        
        # 6. 等待响应
        await asyncio.sleep(10)
        
        # 7. 关闭连接
        connector.close()

    if __name__ == "__main__":
        asyncio.run(main())

下一步
------

- 阅读 `核心概念 <core_concepts>`_ 了解 SDK 的核心概念
- 查看 `API 参考 <api_reference/index>`_ 了解详细的 API 文档
- 探索 `使用示例 <usage_examples/index>`_ 学习更多使用场景
- 了解 `厂商实现 <vendor_implementations/index>`_ 支持的设备