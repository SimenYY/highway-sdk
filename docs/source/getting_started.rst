快速开始
==========

本指南将帮助您快速上手 Highway SDK，展示如何使用 SDK 连接设备、发送命令和处理响应。

基本使用流程
-------------

1. **配置日志** - 设置 SDK 的日志输出
2. **连接设备** - 通过厂商设备类或注册表工厂创建并连接设备
3. **调用 API** - 使用设备方法采集数据或下发控制
4. **处理响应** - 通过 ``Response`` 对象获取结果或错误
5. **关闭连接** - 退出 ``async with`` 上下文自动断开

示例代码
--------

下面是一个最简示例，连接丰海 CMS 设备并获取当前播放项：

.. code-block:: python

    import asyncio
    from highway_sdk import FengHaiDevice

    async def main():
        async with await FengHaiDevice.connect("192.168.1.100", 8888) as device:
            result = await device.get_play_item()
            if result.status == "success":
                print(f"播放项: {result.data}")
            else:
                print(f"获取失败: {result.message}")

    if __name__ == "__main__":
        asyncio.run(main())

通过注册表动态创建设备
-----------------------

适合配置驱动的物联网平台场景：

.. code-block:: python

    import asyncio
    from highway_sdk import connect_device, list_vendors

    async def main():
        # 查看已注册厂商
        for v in list_vendors():
            print(f"{v.name}: {v.display_name} ({v.device_type})")

        # 通过厂商标识符连接设备
        device = await connect_device("fenghai", "192.168.1.100", 8888)
        try:
            brightness = await device.get_brightness()
            print(f"亮度: {brightness.data}")
        finally:
            await device.disconnect()

    asyncio.run(main())

配置日志
---------

库本身不配置日志输出，应用负责配置：

.. code-block:: python

    import logging
    from highway_sdk import get_logger

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    )

    logger = get_logger("highway_sdk.transport")
    logger.info("应用启动")

异常处理
--------

SDK 异常基类为 ``HighwaySDKError``，连接异常基类为 ``DeviceConnectionError``：

.. code-block:: python

    from highway_sdk.core.exceptions import (
        HighwaySDKError,
        DeviceConnectionError,
        ConnectionTimeoutError,
        ResponseTimeoutError,
    )

    try:
        async with await FengHaiDevice.connect("192.168.1.100", 8888) as device:
            await device.get_brightness()
    except ConnectionTimeoutError:
        print("连接超时")
    except ResponseTimeoutError:
        print("响应超时")
    except DeviceConnectionError as e:
        print(f"连接失败: {e}")
    except HighwaySDKError as e:
        print(f"SDK 错误: {e}")

下一步
------

- 阅读 `核心概念 <core_concepts>`_ 了解 SDK 的核心概念
- 查看 `API 参考 <api_reference/index>`_ 了解详细的 API 文档
- 了解 `厂商实现 <vendor_implementations/index>`_ 支持的设备
