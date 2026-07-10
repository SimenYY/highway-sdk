"""诺瓦（Nova）CMS 设备使用示例。

诺瓦 CMS 协议特点：
- 帧结构：起始符 + 指令 + 数据 + CRC16 + 结束符
- 文件传输：分块发送（send_file_name → send_file_content）
- 播放列表：通过 select_play_list 指定 ID 播放

运行方式：
    poetry run python examples/demo_nova.py
"""

import asyncio

from highway_sdk import NovaCms
from highway_sdk.core.exceptions import (
    ConnectionLostError,
    ConnectionTimeoutError,
    DeviceOperationError,
    ResponseTimeoutError,
)
from highway_sdk.vendors.cms import TextLayout
from highway_sdk.vendors.cms.tags import CmsPlayItem


async def main():
    """诺瓦 CMS 设备完整使用示例。"""
    print("=" * 60)
    print("诺瓦（Nova）CMS 设备示例")
    print("=" * 60)

    host = "127.0.0.1"
    port = 9002

    try:
        async with await NovaCms.connect(host, port, timeout=3.0) as device:
            print(f"\n[已连接] {device.__class__.__name__} @ {host}:{port}")

            # ----------------------------------------------------------
            # 1. 获取亮度信息
            # ----------------------------------------------------------
            print("\n--- 1. 获取亮度信息 ---")
            try:
                data = await device.get_brightness()
                print(f"  亮度值: {data['brightness']}%")
                print(f"  控制模式: {data['brightness_mode']}")
                print(f"  采集时间: {data['timestamp']}")
            except DeviceOperationError as e:
                print(f"  获取失败: {e}")

            # ----------------------------------------------------------
            # 2. 获取当前播放项
            # ----------------------------------------------------------
            print("\n--- 2. 获取当前播放项 ---")
            try:
                data = await device.get_play_item()
                item = data["play_item"]
                print(f"  原始文本: {data['orig_play_item']}")
                if item:
                    print(f"  文本: {item['text']}")
                    print(f"  图片: {item['image_name']}")
            except DeviceOperationError as e:
                print(f"  获取失败: {e}")

            # ----------------------------------------------------------
            # 3. 获取播放列表
            # ----------------------------------------------------------
            print("\n--- 3. 获取播放列表 ---")
            try:
                data = await device.get_play_list()
                # Nova 0x3B 响应为类 INI 文本，结构化解析未实现，仅展示原始文本
                orig = data.get("orig_play_list") or "(空)"
                print(f"  原始内容:\n{orig}")
            except DeviceOperationError as e:
                print(f"  获取失败: {e}")

            # ----------------------------------------------------------
            # 4. 下发播放列表
            # ----------------------------------------------------------
            print("\n--- 4. 下发播放列表 ---")
            items = [
                CmsPlayItem(text="注意安全", font="宋体", font_size=24, font_color="#FFFF00", duration=10),
            ]
            try:
                await device.set_play_list(items=items, file_name="play001.lst")
                print("  下发成功")
            except DeviceOperationError as e:
                print(f"  下发失败: {e}")

            # ----------------------------------------------------------
            # 5. 查询屏幕分辨率（配合 TextLayout 计算居中布局）
            # ----------------------------------------------------------
            print("\n--- 5. 查询屏幕分辨率 ---")
            try:
                width, height = await device.get_screen_size()
                print(f"  屏幕分辨率: {width} x {height} (像素)")
            except DeviceOperationError as e:
                print(f"  查询失败: {e}")
                width, height = 96, 32  # 回退默认值

            # ----------------------------------------------------------
            # 6. 下发居中播放列表（使用 TextLayout 自动计算字号和坐标）
            # ----------------------------------------------------------
            # Nova 任意正整数字号，无需 size_range
            print("\n--- 6. 下发居中播放列表（TextLayout 自动布局） ---")
            try:
                layout = TextLayout(
                    "前方施工 请减速慢行 注意行车安全",
                    w=width,
                    h=height,
                )
                result = layout.build()
                print(f"  适配字号: {result.size}")
                print(f"  居中坐标: ({result.x}, {result.y})")
                print(f"  文本占用: {result.text_width}x{result.text_height}")
                print(f"  换行后文本: {result.text!r}")

                items = [
                    CmsPlayItem(
                        text=result.text,
                        font="宋体",
                        font_size=result.size,
                        font_color="#FFFF00",
                        duration=15,
                        x=result.x,
                        y=result.y,
                    ),
                ]
                await device.set_play_list(items=items, file_name="play001.lst")
                print("  下发成功")
            except DeviceOperationError as e:
                print(f"  下发失败: {e}")

    except ConnectionTimeoutError:
        print(f"[错误] 连接超时：设备 {host}:{port} 不可达")
    except ConnectionLostError:
        print("[错误] 连接断开：网络中断或设备重启")
    except ResponseTimeoutError:
        print("[错误] 响应超时：设备繁忙或协议不匹配")
    except Exception as e:
        print(f"[错误] {e}")


if __name__ == "__main__":
    asyncio.run(main())
