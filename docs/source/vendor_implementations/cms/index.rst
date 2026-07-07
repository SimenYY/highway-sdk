CMS厂商实现
============

CMS (Variable Message Sign) 设备厂商实现，提供了多种CMS设备厂商的协议实现。

.. toctree::
   :maxdepth: 2
   :caption: CMS厂商实现

   fenghai

CMS厂商实现概述
----------------

Highway SDK支持多种CMS设备厂商，包括丰海、电明、诺瓦、三思和显科，为每种厂商提供了统一的API接口。

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

各厂商实现详情请参考 :doc:`/api_reference/devices/cms`。其中丰海有独立的厂商实现文档：:doc:`fenghai`。

厂商清单：

- **丰海 (FengHai)** — 国内知名 CMS 厂商，支持播放列表上传即播放（详见 :doc:`fenghai`）
- **电明 (DianMing)** — 使用 SET_PLAY_LIST_AND_PLAY_REQ 单指令完成下发并播放
- **Nova** — 三步式下发：send_file_name + send_file_content + select_play_list
- **三思 (SanSi)** — 上传即播放（与丰海协议格式一致，差异在地址字段与响应 what 字段）
- **显科 (XianKe)** — 两步式：upload_file + select_play_list

扩展新CMS厂商实现
------------------

要扩展新的CMS厂商实现，需要：

1. 在 `highway_sdk/vendors/cms/` 目录下创建新的厂商目录
2. 实现以下核心文件：
   - `spec.py` - 协议规范，定义指令码（What 枚举）、帧结构、CRC 计算、转义规则
   - `codec.py` - 编解码器，继承 `BaseCodec`，使用 `@BaseCodec.register(What.XXX)` 注册解码器
   - `device.py` - 设备客户端，继承 `BaseDevice[VendorCodec]`，实现数据采集与控制 API
3. 在厂商 `__init__.py` 中导出 `metadata`（`VendorMetadata` 实例），SDK 会在 `vendors/__init__.py` 自动注册
4. 编写测试用例（参考 `tests/vendors/cms/`）
5. 更新文档

如果您有兴趣贡献新的CMS厂商实现，欢迎提交PR或联系项目维护者。