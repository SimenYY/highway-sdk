VD设备类型
============

VD (Vehicle Detector) 是车检器设备，用于检测车辆流量、速度、占有率等信息，是高速公路智能交通系统的重要组成部分。

VD设备概述
------------

VD设备通过各种传感器技术检测车辆，收集交通数据，为交通管理系统提供决策依据。

**主要功能**：

- 车辆流量检测
- 车辆速度检测
- 车辆占有率检测
- 车道车辆检测
- 车型分类
- 事件检测（如交通拥堵、事故等）

**设备类型**：

- **环形线圈检测器** - 使用环形线圈检测车辆
- **微波检测器** - 使用微波技术检测车辆
- **视频检测器** - 使用视频图像处理技术检测车辆
- **红外检测器** - 使用红外技术检测车辆
- **激光检测器** - 使用激光技术检测车辆

VD设备通信协议
----------------

VD设备通常使用以下通信协议：

- **TCP/IP协议** - 大多数现代VD设备使用TCP/IP协议通信
- **串口协议** - 部分传统VD设备使用串口协议通信
- **CAN总线** - 部分VD设备使用CAN总线通信

**协议功能**：

- 设备状态查询
- 设备配置
- 数据采集
- 事件上报
- 固件升级

VD设备支持状态
----------------

目前，Highway SDK的VD设备支持正在开发中，尚未正式发布。

我们计划在未来版本中添加VD设备支持，包括：

- 主流VD设备厂商的协议实现
- 统一的VD设备API接口
- 数据采集和处理功能
- 事件处理机制

VD设备API规划
---------------

规划中的VD设备API将包括：

1. **VDProtocol** - VD设备协议基类
2. **VDData** - VD数据结构，包含流量、速度、占有率等信息
3. **VDStatus** - VD设备状态
4. **VDConfig** - VD设备配置

**使用示例（规划）**：

.. code-block:: python

    import asyncio
    from highway_sdk.vendors.vd.vendor1.protocol import VmVendor1Protocol
    from highway_sdk.core.connectors import TCPReconnectingConnector
    from highway_sdk.core.log import LoguruConfig

    # 配置日志
    LoguruConfig.intercept_logging(["*"])
    log_config = LoguruConfig(name="vd-vendor1", level="DEBUG")
    log_config.set_console()

    # 自定义VD协议类
    class MyVDProtocol(VmVendor1Protocol):
        """厂商1 VD协议处理类"""
        def on_data_received(self, data):
            """处理VD数据"""
            print(f"收到VD数据: {data}")

    async def main():
        # 创建连接器
        connector = TCPReconnectingConnector(
            host="192.168.1.200",
            port=9999,
            protocol_cls=MyVDProtocol
        )
        
        # 建立连接
        await connector.create()
        
        # 配置VD设备
        connector.protocol.configure_sampling_rate(60)
        
        # 等待接收数据
        await asyncio.sleep(60)
        
        # 关闭连接
        connector.close()

    if __name__ == "__main__":
        asyncio.run(main())

扩展VD设备支持
----------------

要扩展VD设备支持，需要：

1. 在 `highway_sdk/vendors/vd/` 目录下创建厂商实现目录
2. 实现以下文件：
   - `protocol.py` - VD设备协议实现
   - `parser.py` - 数据解析器
   - `spec.py` - 协议规范
3. 编写测试用例
4. 更新文档

如果您有兴趣贡献VD设备的实现，欢迎提交PR或联系项目维护者。