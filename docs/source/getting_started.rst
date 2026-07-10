快速开始
==========

本指南将帮助您快速上手 Highway SDK，展示如何使用 SDK 连接设备、发送命令和处理异常。

基本使用流程
-------------

1. **配置日志** - 设置 SDK 的日志输出
2. **连接设备** - 通过厂商设备类或注册表工厂创建并连接设备
3. **调用 API** - 使用设备方法采集数据或下发控制
4. **处理异常** - 失败抛 ``HighwaySDKError`` 子类异常，调用方按业务场景捕获
5. **关闭连接** - 退出 ``async with`` 上下文自动断开

示例代码
--------

下面是一个最简示例，连接丰海 CMS 设备并获取当前播放项：

.. code-block:: python

    import asyncio
    from highway_sdk import FengHaiCms
    from highway_sdk.core.exceptions import DeviceOperationError

    async def main():
        async with await FengHaiCms.connect("192.168.1.100", 8888) as device:
            try:
                # 数据采集方法成功返回 dict（CmsTags.model_dump(exclude_none=True)）
                data = await device.get_play_item()
                print(f"播放项: {data['play_item']}")
            except DeviceOperationError as e:
                # 业务失败：设备返回错误响应、协议版本不匹配、数据损坏等
                print(f"获取失败: {e}")

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
            # get_brightness 成功返回 dict，失败抛 DeviceOperationError
            brightness = await device.get_brightness()
            print(f"亮度: {brightness}")
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

Highway SDK 采用 **Pythonic 异常模式**：成功返回业务数据（``dict`` 或 ``None``），失败抛 ``HighwaySDKError`` 子类异常。SDK 异常基类为 ``HighwaySDKError``，连接异常基类为 ``DeviceConnectionError``，业务失败异常为 ``DeviceOperationError``：

.. code-block:: python

    from highway_sdk.core.exceptions import (
        HighwaySDKError,
        DeviceConnectionError,
        DeviceOperationError,
        ConnectionTimeoutError,
        ResponseTimeoutError,
    )

    try:
        async with await FengHaiCms.connect("192.168.1.100", 8888) as device:
            # 数据采集返回 dict，失败抛 DeviceOperationError
            data = await device.get_brightness()
            print(f"亮度: {data['brightness']}%")
            # 控制方法成功返回 None，失败抛 DeviceOperationError
            await device.set_brightness(brightness=20)
    except ConnectionTimeoutError:
        print("连接超时")
    except ResponseTimeoutError:
        print("响应超时")
    except DeviceOperationError as e:
        # 业务失败：设备返回错误响应、协议版本不匹配、数据损坏等
        print(f"操作失败: {e}")
    except DeviceConnectionError as e:
        # DeviceConnectionError 是连接异常基类，捕获它不会误吞 asyncio/socket
        # 层抛出的内建 ConnectionError（OSError 子类）
        print(f"连接失败: {e}")
    except HighwaySDKError as e:
        print(f"SDK 错误: {e}")

下一步
------

- 阅读 `核心概念 <core_concepts>`_ 了解 SDK 的核心概念
- 查看 `API 参考 <api_reference/index>`_ 了解详细的 API 文档
- 了解 `厂商实现 <vendor_implementations/index>`_ 支持的设备
