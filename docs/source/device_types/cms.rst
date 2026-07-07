CMS设备类型
============

CMS (Variable Message Sign) 是可变信息标志设备，用于在高速公路上显示可变信息，如路况、天气、事故信息等。

CMS设备概述
------------

CMS设备是高速公路智能交通系统的重要组成部分，通过显示实时交通信息，帮助驾驶员做出正确的驾驶决策，提高道路通行效率和安全性。

**主要功能**：

- 显示实时路况信息
- 显示天气信息
- 显示事故、施工等特殊信息
- 显示速度限制
- 显示车道控制信息

**设备类型**：

- **门架式CMS** - 安装在高速公路上方的门架上
- **立柱式CMS** - 安装在高速公路旁的立柱上
- **隧道式CMS** - 安装在隧道内
- **移动式CMS** - 安装在车辆上，用于临时信息发布

CMS设备通信协议
----------------

不同的CMS设备厂商使用不同的通信协议，Highway SDK封装了这些协议，提供统一的API接口。

**协议功能**：

- 设备状态查询
- 设备控制
- 信息发布（播放列表下发）
- 媒体文件管理
- 亮度控制
- 模式切换

CMS设备API使用
---------------

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

            # 下发播放列表并播放
            from highway_sdk.vendors.cms.tags import CmsPlayItem
            items = [
                CmsPlayItem(text="注意行车安全", font="黑体", font_size=32, font_color="#FF0000", duration=10),
            ]
            await device.set_play_list(items)

    if __name__ == "__main__":
        asyncio.run(main())

文字居中显示（TextLayout）
----------------------------

CMS 显示屏尺寸有限，文字内容需要根据显示区域自动选择合适的字号、换行和居中坐标，
确保内容完整可见且上下左右居中。SDK 提供 ``TextLayout`` 厂商无关工具实现该布局计算。

字符宽度规则：
    - ASCII 字符（半角）：字号 / 2
    - 非 ASCII 字符（如中文全角）：字号

算法步骤：
    1. 二分查找最大字号使文字完整显示在 w×h 区域
    2. 逐字符遍历，超宽时自动换行（``\\n`` 分隔）
    3. 计算居中坐标 ``x = (w - text_w) // 2, y = (h - text_h) // 2``

.. code-block:: python

    import asyncio
    from highway_sdk import FengHaiDevice
    from highway_sdk.vendors.cms import TextLayout
    from highway_sdk.vendors.cms.tags import CmsPlayItem

    async def main():
        async with await FengHaiDevice.connect("192.168.1.100", 8888) as device:
            # 假设显示屏分辨率 96x32 像素
            # 丰海 FontSize 枚举固定为 16/24/32/48/64，必须传入 size_range
            layout = TextLayout(
                "前方施工 请减速慢行 注意安全",
                w=96,
                h=32,
                size_range=[16, 24, 32, 48, 64],
            )
            result = layout.build()
            print(f"适配字号: {result.size}")           # 16
            print(f"居中坐标: ({result.x}, {result.y})")
            print(f"文本占用: {result.text_width}x{result.text_height}")
            print(f"换行后: {result.text!r}")

            items = [
                CmsPlayItem(
                    text=result.text,
                    font="宋体",
                    font_size=result.size,
                    font_color="#FF0000",
                    duration=15,
                    x=result.x,
                    y=result.y,
                ),
            ]
            await device.set_play_list(items)

    if __name__ == "__main__":
        asyncio.run(main())

厂商字号差异
~~~~~~~~~~~~~~~~

- **电明 / 丰海 / 三思 / 显科**：FontSize 为固定枚举（16/24/32/48/64），调用 ``TextLayout``
  时必须传入 ``size_range=[16, 24, 32, 48, 64]``，工具会从适配字号中选取最接近且不超出的列表值
- **Nova**：任意正整数字号，无需 ``size_range``；可调用 ``device.get_screen_size()`` 查询
  设备实际分辨率，作为 ``w`` / ``h`` 参数

TextLayout 字段说明
~~~~~~~~~~~~~~~~~~~

``TextLayout(text, *, w, h, max_size=None, min_size=8, size_range=None, word_space=0, line_space=0)``

- ``text``：要显示的文本内容，不能为空
- ``w`` / ``h``：显示区域宽高（像素），必须为正
- ``max_size``：最大字号，默认 ``min(w, h)``
- ``min_size``：最小字号，默认 8，下限为 ``MIN_SIZE`` 类常量
- ``size_range``：设备支持的字号列表；提供时工具会从中选取最接近适配字号的列表值
- ``word_space`` / ``line_space``：字间距 / 行间距（像素），默认 0

``TextLayoutResult`` 包含字段：``text``、``lines``、``size``、``x``、``y``、
``text_width``、``text_height``，分别对应换行后文本、行列表、适配字号、居中坐标、文本占用尺寸。
调用方负责将结果填入 ``CmsPlayItem`` 的 ``text`` / ``font_size`` / ``x`` / ``y`` 字段。

CMS设备厂商实现
----------------

Highway SDK支持多种CMS设备厂商，详见 :doc:`/api_reference/devices/cms` 和 :doc:`/vendor_implementations/cms/index`。

厂商清单：

- **电明 (DianMing)** — 使用 SET_PLAY_LIST_AND_PLAY_REQ 单指令完成下发并播放
- **丰海 (FengHai)** — 上传即播放（委托 upload_file）
- **Nova** — 三步式：send_file_name + send_file_content + select_play_list
- **三思 (SanSi)** — 上传即播放（委托 upload_file）
- **显科 (XianKe)** — 两步式：upload_file + select_play_list

扩展CMS设备支持
----------------

要扩展新的CMS设备厂商支持，需要：

1. 在 `highway_sdk/vendors/cms/` 目录下创建厂商实现目录
2. 实现以下核心文件：
   - `spec.py` - 协议规范，定义指令码（What 枚举）、帧结构、CRC 计算、转义规则
   - `codec.py` - 编解码器，继承 `BaseCodec`，使用 `@BaseCodec.register(What.XXX)` 注册解码器
   - `device.py` - 设备客户端，继承 `BaseDevice[VendorCodec]`，实现数据采集与控制 API
3. 在厂商 `__init__.py` 中导出 `metadata`（`VendorMetadata` 实例），SDK 会在 `vendors/__init__.py` 自动注册
4. 编写测试用例（参考 `tests/vendors/cms/`）
5. 更新文档，添加新厂商实现的说明
