丰海CMS厂商实现
================

丰海是国内知名的CMS设备厂商，Highway SDK提供了丰海CMS设备的完整协议实现。

丰海CMS设备概述
----------------

丰海CMS设备采用先进的LED显示技术，具有高亮度、高可靠性、易于维护等特点，广泛应用于高速公路、城市道路等场景。

**设备特点**：

- 高亮度LED显示，适应各种天气条件
- 模块化设计，易于维护和扩展
- 支持多种通信协议
- 支持远程管理和控制
- 支持媒体文件管理

丰海CMS设备协议
----------------

丰海CMS设备使用自定义的TCP协议进行通信，Highway SDK封装了该协议，提供统一的API接口。

**协议功能**：

- 设备状态查询
- 设备控制
- 信息发布
- 媒体文件管理
- 亮度控制
- 模式切换

丰海CMS API使用
----------------

**核心类**：

- **FengHaiDevice** - 丰海CMS设备客户端，继承 BaseDevice[FengHaiCodec]
- **FengHaiCodec** - 丰海CMS编解码器，继承 BaseCodec
- **Frame** - 丰海CMS帧数据结构，继承 CMSFrame

**使用示例**：

.. code-block:: python

    import asyncio
    from highway_sdk.vendors.cms.fenghai.device import FengHaiDevice

    async def main():
        # 连接设备
        async with await FengHaiDevice.connect("192.168.1.100", 8888) as device:
            # 获取当前播放项
            result = await device.get_play_item()
            print(f"播放项: {result}")

            # 获取亮度和模式
            result = await device.get_brightness()
            print(f"亮度: {result}")

            # 设置亮度
            result = await device.set_brightness(20)
            print(f"设置结果: {result}")

            # 下发播放列表并播放
            content = "[playlist]\\r\\nitem_no=1\\r\\nitem0=300,1,0,..."
            result = await device.set_play_list(content)
            print(f"下发结果: {result}")

    if __name__ == "__main__":
        asyncio.run(main())

丰海CMS设备方法
----------------

FengHaiDevice 提供以下设备操作方法：

- ``get_play_item()`` - 获取当前播放项
- ``get_play_list(play_id=0)`` - 获取当前播放列表
- ``get_brightness()`` - 获取亮度和模式
- ``set_brightness(brightness)`` - 设置亮度
- ``upload_file(content, file_name="play.lst")`` - 上传播放列表文件
- ``set_play_list(content, file_name="play.lst")`` - 下发播放列表并播放（委托 upload_file，上传即播放）

丰海CMS测试用例
----------------

Highway SDK为丰海CMS实现提供了完整的测试用例，包括：

- **test_fenghai_protocol.py** - 协议帧序列化与解析测试
- **test_fenghai_real_packets.py** - 真实报文解析测试（基于实际设备通信日志）
- **test_fenghai_get_play_list_real_packet.py** - 获取播放列表真实报文测试
- **test_fenghai_set_play_list_real_packet.py** - 下发播放列表真实报文测试

**运行测试**：

.. code-block:: bash

    pytest tests/vendors/cms/fenghai/ -v