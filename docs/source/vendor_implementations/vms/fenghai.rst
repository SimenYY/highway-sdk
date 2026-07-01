丰海VMS厂商实现
================

丰海是国内知名的VMS设备厂商，Highway SDK提供了丰海VMS设备的完整协议实现。

丰海VMS设备概述
----------------

丰海VMS设备采用先进的LED显示技术，具有高亮度、高可靠性、易于维护等特点，广泛应用于高速公路、城市道路等场景。

**设备特点**：

- 高亮度LED显示，适应各种天气条件
- 模块化设计，易于维护和扩展
- 支持多种通信协议
- 支持远程管理和控制
- 支持媒体文件管理

丰海VMS设备协议
----------------

丰海VMS设备使用自定义的TCP协议进行通信，Highway SDK封装了该协议，提供统一的API接口。

**协议功能**：

- 设备状态查询
- 设备控制
- 信息发布
- 媒体文件管理
- 亮度控制
- 模式切换

丰海VMS API使用
----------------

**核心类**：

- **VmsFenghaiProtocol** - 丰海VMS设备协议类
- **FrameFactory** - 丰海VMS帧工厂，用于创建设备通信的请求帧
- **Parser** - 丰海VMS解析器，用于解析设备返回的数据

**使用示例**：

.. code-block:: python

    import asyncio
    from highway_sdk.vendors.vms.fenghai.protocol import VmsFenghaiProtocol
    from highway_sdk.core.connectors import TCPReconnectingConnector

    # 自定义丰海协议类
    class MyFenghaiProtocol(VmsFenghaiProtocol):
        """丰海VMS协议处理类"""
        def on_message_parsed(self, tags):
            """处理丰海设备响应"""
            print(f"丰海设备响应: {tags}")

    async def main():
        # 创建连接器
        connector = TCPReconnectingConnector(
            host="192.168.1.100",
            port=8888,
            protocol_cls=MyFenghaiProtocol
        )
        
        # 建立连接
        await connector.create()
        
        # 发送命令
        connector.protocol.get_play_item()
        connector.protocol.get_brightness_and_mode()
        connector.protocol.set_brightness(20)
        
        # 等待响应
        await asyncio.sleep(10)
        
        # 关闭连接
        connector.close()

    if __name__ == "__main__":
        asyncio.run(main())

丰海VMS媒体管理
----------------

丰海VMS设备支持媒体文件管理，包括文件上传、下载、删除等功能。

**媒体管理功能**：

- 上传媒体文件
- 下载媒体文件
- 删除媒体文件
- 列出媒体文件
- 设置媒体文件播放

**使用示例**：

.. code-block:: python

    import asyncio
    from highway_sdk.vendors.vms.fenghai.protocol import VmsFenghaiProtocol
    from highway_sdk.core.connectors import TCPReconnectingConnector

    # 自定义丰海协议类
    class MyFenghaiProtocol(VmsFenghaiProtocol):
        """丰海VMS协议处理类"""
        def on_message_parsed(self, tags):
            """处理丰海设备响应"""
            print(f"丰海设备响应: {tags}")

    async def main():
        # 创建连接器
        connector = TCPReconnectingConnector(
            host="192.168.1.100",
            port=8888,
            protocol_cls=MyFenghaiProtocol
        )
        
        # 建立连接
        await connector.create()
        
        # 下载文件
        connector.protocol.download_file(file_name="play.lst")
        
        # 上传文件
        file_content = "[playlist]\nitem_no=1\nitem0=300,1,0,\\C000000\\c25500000000\\b00000000000\\fs2424测试内容"
        connector.protocol.upload_file(content=file_content, file_name="play.lst")
        
        # 等待响应
        await asyncio.sleep(10)
        
        # 关闭连接
        connector.close()

    if __name__ == "__main__":
        asyncio.run(main())

丰海VMS测试用例
----------------

Highway SDK为丰海VMS实现提供了完整的测试用例，包括：

- **test_factory.py** - 帧工厂测试
- **test_parser.py** - 解析器测试
- **test_media.py** - 媒体管理测试

**运行测试**：

.. code-block:: bash

    pytest tests/vendors/vms/fenghai/ -v