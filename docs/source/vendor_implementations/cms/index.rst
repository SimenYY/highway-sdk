CMS厂商实现
============

CMS (Variable Message Sign) 设备厂商实现，提供了多种CMS设备厂商的协议实现。

.. toctree::
   :maxdepth: 2
   :caption: CMS厂商实现

   fenghai
   nova
   xianke
   sansi

CMS厂商实现概述
----------------

Highway SDK支持多种CMS设备厂商，包括丰海、Nova、Xianke和Sansi等，为每种厂商提供了统一的API接口。

**厂商实现特点**：

- 统一的API接口，屏蔽不同厂商协议的差异
- 完整的协议实现，支持设备的各种功能
- 良好的扩展性，便于添加新的厂商支持
- 完整的测试用例，确保实现的正确性

**主要功能支持**：

- 设备状态查询
- 设备控制
- 信息发布
- 媒体文件管理
- 亮度控制
- 模式切换

丰海 (Fenghai) 厂商实现
------------------------

丰海是国内知名的CMS设备厂商，Highway SDK提供了丰海CMS设备的完整协议实现。

请参考 `fenghai <fenghai>`_ 文档。

Nova 厂商实现
--------------

Nova是另一家知名的CMS设备厂商，Highway SDK提供了Nova CMS设备的完整协议实现。

请参考 `nova <nova>`_ 文档。

Xianke 厂商实现
---------------

Xianke是国内领先的CMS设备厂商，Highway SDK提供了Xianke CMS设备的完整协议实现。

请参考 `xianke <xianke>`_ 文档。

Sansi 厂商实现
--------------

Sansi是知名的照明和显示设备厂商，Highway SDK提供了Sansi CMS设备的完整协议实现。

请参考 `sansi <sansi>`_ 文档。

扩展新CMS厂商实现
------------------

要扩展新的CMS厂商实现，需要：

1. 在 `highway_sdk/vendors/cms/` 目录下创建新的厂商目录
2. 实现以下核心文件：
   - `factory.py` - 帧工厂，用于创建设备通信的请求帧
   - `parser.py` - 解析器，用于解析设备返回的数据
   - `protocol.py` - 协议实现，用于处理设备通信
   - `spec.py` - 协议规范，定义指令码、帧结构等
   - `media.py` - 媒体管理，用于处理设备的媒体文件
3. 编写测试用例
4. 更新文档

如果您有兴趣贡献新的CMS厂商实现，欢迎提交PR或联系项目维护者。