"""Highway SDK 使用示例。

运行方式：
    poetry run python examples/demo.py
"""

import asyncio

from highway_sdk import (
    DianMingDevice,
    FengHaiDevice,
    NovaDevice,
    SanSiDevice,
    Transport,
    XianKeDevice,
    connect_device,
    create_device,
    get_vendor,
    list_vendors,
)
from highway_sdk.core.exceptions import (
    ConnectionLostError,
    ConnectionTimeoutError,
    ResponseTimeoutError,
)


async def example_basic_usage():
    """基础使用示例：连接设备并获取信息。"""
    print("=" * 60)
    print("示例 1: 基础使用")
    print("=" * 60)

    # 使用上下文管理器自动管理连接
    async with await DianMingDevice.connect("127.0.0.1", 9000) as device:
        # 获取亮度信息
        brightness = await device.get_brightness()
        print(f"亮度信息: {brightness}")

        # 获取当前播放项
        play_item = await device.get_play_item()
        print(f"当前播放: {play_item}")

        # 获取播放列表
        play_list = await device.get_play_list(play_id=0)
        print(f"播放列表: {play_list}")


async def example_custom_transport():
    """自定义传输层示例：配置自动重连。"""
    print("\n" + "=" * 60)
    print("示例 2: 自定义传输层（自动重连）")
    print("=" * 60)

    # 创建带自动重连的传输层
    transport = Transport(
        "127.0.0.1",
        9000,
        timeout=5.0,
        auto_reconnect=True,
        reconnect_interval=3.0,
        max_reconnect_attempts=5,
    )

    await transport.connect()
    device = FengHaiDevice(transport)

    try:
        # 执行操作
        brightness = await device.get_brightness()
        print(f"亮度信息: {brightness}")

        # 模拟网络中断后自动重连
        print("等待 10 秒模拟网络中断...")
        await asyncio.sleep(10)

        # 自动重连后继续操作
        play_item = await device.get_play_item()
        print(f"当前播放: {play_item}")

    finally:
        await device.disconnect()


async def example_multiple_vendors():
    """多厂商设备示例：同时管理多个厂商设备。"""
    print("\n" + "=" * 60)
    print("示例 3: 多厂商设备管理")
    print("=" * 60)

    # 设备配置
    devices_config = [
        {"vendor": "dianming", "host": "127.0.0.1", "port": 9000},
        {"vendor": "fenghai", "host": "127.0.0.1", "port": 9001},
        {"vendor": "nova", "host": "127.0.0.1", "port": 9002},
        {"vendor": "sansi", "host": "127.0.0.1", "port": 9003},
        {"vendor": "xianke", "host": "127.0.0.1", "port": 9004},
    ]

    # 厂商设备类映射
    vendor_map = {
        "dianming": DianMingDevice,
        "fenghai": FengHaiDevice,
        "nova": NovaDevice,
        "sansi": SanSiDevice,
        "xianke": XianKeDevice,
    }

    # 连接所有设备
    devices = []
    for config in devices_config:
        try:
            vendor = config["vendor"]
            device_class = vendor_map[vendor]
            device = await device_class.connect(config["host"], config["port"])
            devices.append((vendor, device))
            print(f"✓ {vendor} 设备已连接")
        except Exception as e:
            print(f"✗ {vendor} 设备连接失败: {e}")

    # 批量获取亮度信息
    print("\n批量获取亮度信息:")
    for vendor, device in devices:
        try:
            brightness = await device.get_brightness()
            print(f"  {vendor}: {brightness}")
        except Exception as e:
            print(f"  {vendor}: 获取失败 - {e}")

    # 断开所有设备
    for vendor, device in devices:
        await device.disconnect()
        print(f"✓ {vendor} 设备已断开")


async def example_error_handling():
    """错误处理示例：优雅处理各种异常。"""
    print("\n" + "=" * 60)
    print("示例 4: 错误处理")
    print("=" * 60)

    try:
        async with await DianMingDevice.connect(
            "127.0.0.1",
            9000,
            timeout=2.0,
        ) as device:
            await device.get_brightness()

    except ConnectionTimeoutError:
        print("连接超时：设备可能离线或网络不通")
    except ConnectionLostError:
        print("连接断开：网络中断或设备重启")
    except ResponseTimeoutError:
        print("响应超时：设备繁忙或协议不匹配")
    except Exception as e:
        print(f"未知错误: {e}")


async def example_custom_transport_factory():
    """自定义传输层工厂示例。"""
    print("\n" + "=" * 60)
    print("示例 5: 自定义传输层工厂")
    print("=" * 60)

    def custom_transport_factory(host: str, port: int, **kwargs):
        """自定义传输层工厂：添加日志或特殊配置。"""
        print(f"创建传输层: {host}:{port}")
        return Transport(
            host,
            port,
            timeout=10.0,  # 自定义超时时间
            auto_reconnect=True,
            **kwargs,
        )

    device = await NovaDevice.connect(
        "127.0.0.3",
        9000,
        transport_factory=custom_transport_factory,
    )

    try:
        brightness = await device.get_brightness()
        print(f"亮度信息: {brightness}")
    finally:
        await device.disconnect()


async def example_concurrent_operations():
    """并发操作示例：同时执行多个设备操作。"""
    print("\n" + "=" * 60)
    print("示例 6: 并发操作")
    print("=" * 60)

    async with await DianMingDevice.connect("127.0.0.1", 9000) as device:
        # 并发执行多个操作
        results = await asyncio.gather(
            device.get_brightness(),
            device.get_play_item(),
            device.get_play_list(),
            return_exceptions=True,
        )

        brightness, play_item, play_list = results

        print(f"亮度: {brightness}")
        print(f"播放项: {play_item}")
        print(f"播放列表: {play_list}")


async def example_vendor_registry():
    """厂商注册表示例：动态创建设备（物联网平台集成）。"""
    print("\n" + "=" * 60)
    print("示例 7: 厂商注册表（物联网平台集成）")
    print("=" * 60)

    # 1. 查看所有已注册厂商
    print("\n已注册厂商列表:")
    vendors = list_vendors()
    for vendor in vendors:
        print(f"  - {vendor.name}: {vendor.display_name} ({vendor.device_type})")

    # 2. 获取特定厂商信息
    print("\n获取电明厂商信息:")
    dianming = get_vendor("dianming")
    print(f"  名称: {dianming.display_name}")
    print(f"  类型: {dianming.device_type}")
    print(f"  描述: {dianming.description}")

    # 3. 使用注册表创建设备（未连接）
    print("\n使用注册表创建设备实例:")
    device = create_device("dianming", "127.0.0.1", 9000)
    print(f"  创建成功: {device.__class__.__name__}")
    print(f"  传输层: {device.transport.host}:{device.transport.port}")

    # 4. 使用注册表连接设备（配置驱动场景）
    print("\n使用注册表连接设备:")
    try:
        device = await connect_device("fenghai", "127.0.0.1", 9001)
        print(f"  连接成功: {device.__class__.__name__}")

        # 执行操作
        brightness = await device.get_brightness()
        print(f"  亮度信息: {brightness}")

        await device.disconnect()
        print("  已断开连接")
    except Exception as e:
        print(f"  连接失败: {e}")

    # 5. 物联网平台配置驱动示例
    print("\n物联网平台配置驱动示例:")
    platform_config = [
        {"vendor": "dianming", "host": "127.0.0.1", "port": 9000, "name": "CMS-001"},
        {"vendor": "fenghai", "host": "127.0.0.1", "port": 9001, "name": "CMS-002"},
        {"vendor": "nova", "host": "127.0.0.1", "port": 9002, "name": "CMS-003"},
    ]

    devices = []
    for config in platform_config:
        try:
            device = await connect_device(
                vendor=config["vendor"],
                host=config["host"],
                port=config["port"],
            )
            devices.append((config["name"], device))
            print(f"  ✓ {config['name']} ({config['vendor']}) 已连接")
        except Exception as e:
            print(f"  ✗ {config['name']} ({config['vendor']}) 连接失败: {e}")

    # 批量操作
    print("\n批量获取设备信息:")
    for name, device in devices:
        try:
            brightness = await device.get_brightness()
            print(f"  {name}: 亮度={brightness}")
        except Exception as e:
            print(f"  {name}: 获取失败 - {e}")

    # 清理
    for name, device in devices:
        await device.disconnect()
        print(f"  ✓ {name} 已断开")


async def main():
    """运行所有示例。"""
    print("Highway SDK 使用示例\n")

    # 注意：这些示例需要真实的设备或模拟服务器
    # 取消注释以运行特定示例

    await example_basic_usage()
    # await example_custom_transport()
    # await example_multiple_vendors()
    # await example_error_handling()
    # await example_custom_transport_factory()
    # await example_concurrent_operations()
    # await example_vendor_registry()

    print("\n提示：取消注释相应的示例函数以运行测试")
    print("确保设备在线或配置正确的网络环境")


if __name__ == "__main__":
    asyncio.run(main())
