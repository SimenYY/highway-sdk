VMS设备类型
============

VMS (Variable Message Sign) 是可变信息标志设备，用于在高速公路上显示可变信息，如路况、天气、事故信息等。

VMS设备概述
------------

VMS设备是高速公路智能交通系统的重要组成部分，通过显示实时交通信息，帮助驾驶员做出正确的驾驶决策，提高道路通行效率和安全性。

**主要功能**：

- 显示实时路况信息
- 显示天气信息
- 显示事故、施工等特殊信息
- 显示速度限制
- 显示车道控制信息

**设备类型**：

- **门架式VMS** - 安装在高速公路上方的门架上
- **立柱式VMS** - 安装在高速公路旁的立柱上
- **隧道式VMS** - 安装在隧道内
- **移动式VMS** - 安装在车辆上，用于临时信息发布

VMS设备通信协议
----------------

不同的VMS设备厂商使用不同的通信协议，Highway SDK封装了这些协议，提供统一的API接口。

**主要协议类型**：

- **TCP协议** - 大多数VMS设备使用TCP协议通信
- **UDP协议** - 部分VMS设备使用UDP协议通信

**协议功能**：

- 设备状态查询
- 设备控制
- 信息发布
- 媒体文件管理
- 亮度控制
- 模式切换

VMS设备API使用
---------------

使用VMS设备API的基本步骤：

1. 导入VMS设备协议类
2. 创建自定义协议类，继承自厂商协议类
3. 实现设备响应处理方法
4. 创建连接器，连接到设备
5. 发送命令，控制设备
6. 处理设备响应
7. 关闭连接

**示例代码**：

.. code-block:: python

    import asyncio
    from highway_sdk.vendors.vms.fenghai.protocol import VmsFenghaiProtocol
    from highway_sdk.core.connectors import TCPReconnectingConnector
    from highway_sdk.core.log import LoguruConfig

    # 配置日志
    LoguruConfig.intercept_logging(["*"])
    log_config = LoguruConfig(name="fenghai-vms", level="DEBUG")
    log_config.set_console()

    # 使用厂商特定协议
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
        
        # 发送丰海特定命令
        connector.protocol.get_play_item()
        connector.protocol.get_brightness_and_mode()
        
        # 等待响应
        await asyncio.sleep(10)
        
        # 关闭连接
        connector.close()

    if __name__ == "__main__":
        asyncio.run(main())

VMS设备厂商实现
----------------

Highway SDK支持多种VMS设备厂商，包括：

.. toctree::
   :maxdepth: 1
   :caption: VMS厂商实现

   /vendor_implementations/vms/fenghai
   /vendor_implementations/vms/nova
   /vendor_implementations/vms/xianke
   /vendor_implementations/vms/sansi

扩展VMS设备支持
----------------

要扩展新的VMS设备厂商支持，需要：

1. 在 `highway_sdk/vendors/vms/` 目录下创建厂商实现目录
2. 实现以下文件：
   - `factory.py` - 帧工厂，用于创建请求帧
   - `parser.py` - 解析器，用于解析设备响应
   - `protocol.py` - 协议类，用于处理设备通信
   - `spec.py` - 协议规范，定义指令码和帧结构
   - `media.py` - 媒体管理，用于处理媒体文件
3. 在 `highway_sdk/vendors/vms/__init__.py` 中导出新的厂商实现
4. 编写测试用例
5. 更新文档，添加新厂商实现的说明