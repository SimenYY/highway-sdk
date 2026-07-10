"""电明（DianMing）CMS 设备使用示例。

电明 CMS 协议特点：
- 帧结构：STX + 目的地址 + 源地址 + 指令 + 数据 + CRC16 + ETX
- 亮度调节：支持 0-31 手动调节，或自动模式（FFFFFF）
- 播放列表：使用 INI 格式（[PLAYLIST] / ITEM_NO= / ITEM000=）

运行方式：
    poetry run python examples/demo_dianming.py
"""

import asyncio

from highway_sdk import DianMingCms
from highway_sdk.core.exceptions import (
    ConnectionLostError,
    ConnectionTimeoutError,
    DeviceOperationError,
    ResponseTimeoutError,
)
from highway_sdk.vendors.cms import TextLayout
from highway_sdk.vendors.cms.tags import CmsPlayItem


async def main():  # noqa: C901
    """电明 CMS 设备完整使用示例。"""
    print("=" * 60)
    print("电明（DianMing）CMS 设备示例")
    print("=" * 60)

    # 设备连接参数（请根据实际环境修改）
    host = "127.0.0.1"
    port = 9000

    try:
        async with await DianMingCms.connect(host, port, timeout=3.0) as device:
            print(f"\n[已连接] {device.__class__.__name__} @ {host}:{port}")

            # ----------------------------------------------------------
            # 1. 获取亮度信息
            # ----------------------------------------------------------
            print("\n--- 1. 获取亮度信息 ---")
            try:
                data = await device.get_brightness()
                print(f"  亮度值: {data.brightness}%")
                print(f"  控制模式: {data.brightness_mode}")
                print(f"  采集时间: {data.timestamp}")
            except DeviceOperationError as e:
                print(f"  获取失败: {e}")

            # ----------------------------------------------------------
            # 2. 获取当前播放项
            # ----------------------------------------------------------
            print("\n--- 2. 获取当前播放项 ---")
            try:
                data = await device.get_play_item()
                item = data.play_item
                print(f"  原始格式: {data.orig_play_item}")
                if item:
                    print(f"  序号: {item.index}")
                    print(f"  文本: {item.text}")
                    print(f"  字体: {item.font} (大小 {item.font_size})")
                    print(f"  颜色: {item.font_color}")
                    print(f"  停留时间: {item.duration} 秒")
            except DeviceOperationError as e:
                print(f"  获取失败: {e}")

            # ----------------------------------------------------------
            # 3. 获取播放列表
            # ----------------------------------------------------------
            print("\n--- 3. 获取播放列表 ---")
            try:
                data = await device.get_play_list(play_id=0, filename="play00.lst")
                play_list = data.play_list
                print(f"  共 {len(play_list)} 个播放项:")
                for i, item in enumerate(play_list):
                    text = item.text or "(图片)"
                    print(f"    [{i}] {text} (停留 {item.duration}s)")
            except DeviceOperationError as e:
                print(f"  获取失败: {e}")

            # ----------------------------------------------------------
            # 4. 设置亮度（手动模式）
            # ----------------------------------------------------------
            print("\n--- 4. 设置亮度为 20 ---")
            try:
                await device.set_brightness(brightness=20)
                print("  设置成功")
            except DeviceOperationError as e:
                print(f"  设置失败: {e}")

            # ----------------------------------------------------------
            # 5. 设置亮度（自动模式）
            # ----------------------------------------------------------
            print("\n--- 5. 切换为自动亮度模式 ---")
            try:
                await device.set_brightness(brightness=None)
                print("  设置成功")
            except DeviceOperationError as e:
                print(f"  设置失败: {e}")

            # ----------------------------------------------------------
            # 6. 下发播放列表并立即播放
            # ----------------------------------------------------------
            print("\n--- 6. 下发播放列表 ---")
            items = [
                CmsPlayItem(text="前方施工 减速慢行", font="宋体", font_size=32, font_color="#FF0000", duration=15),
            ]
            try:
                await device.set_play_list(items=items, file_name="play.lst")
                print("  下发成功")
            except DeviceOperationError as e:
                print(f"  下发失败: {e}")

            # ----------------------------------------------------------
            # 7. 下发居中播放列表（使用 TextLayout 自动计算字号和坐标）
            # ----------------------------------------------------------
            # 电明 FontSize 枚举固定为 16/24/32/48/64，必须传入 size_range
            # 让 TextLayout 从适配字号中选取最接近且不超出的列表值
            print("\n--- 7. 下发居中播放列表（TextLayout 自动布局） ---")
            try:
                layout = TextLayout(
                    "前方施工 请减速慢行 注意安全",
                    w=96,  # 显示区域宽（像素），请根据实际设备调整
                    h=32,  # 显示区域高（像素）
                    size_range=[16, 24, 32, 48, 64],
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
                        font_color="#FF0000",
                        duration=15,
                        x=result.x,
                        y=result.y,
                    ),
                ]
                await device.set_play_list(items=items, file_name="play.lst")
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
