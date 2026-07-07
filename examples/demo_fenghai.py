"""丰海（FengHai）CMS 设备使用示例。

丰海 CMS 协议特点：
- 帧结构：起始符 + 指令 + 数据 + CRC16 + 结束符
- 亮度调节：0-31 范围，不支持自动模式
- 播放列表：通过 upload_file 上传，支持自定义文件名

运行方式：
    poetry run python examples/demo_fenghai.py
"""

import asyncio

from highway_sdk import FengHaiDevice
from highway_sdk.core.exceptions import (
    ConnectionLostError,
    ConnectionTimeoutError,
    DeviceOperationError,
    ResponseTimeoutError,
)


async def main():
    """丰海 CMS 设备完整使用示例。"""
    print("=" * 60)
    print("丰海（FengHai）CMS 设备示例")
    print("=" * 60)

    host = "127.0.0.1"
    port = 9001

    try:
        async with await FengHaiDevice.connect(host, port, timeout=3.0) as device:
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
                print(f"  原始格式: {data['orig_play_item']}")
                if item:
                    print(f"  序号: {item['index']}")
                    print(f"  文本: {item['text']}")
                    print(f"  颜色: {item['font_color']}")
                    print(f"  图片: {item['image_name']}")
                    print(f"  停留时间: {item['duration']} 秒")
            except DeviceOperationError as e:
                print(f"  获取失败: {e}")

            # ----------------------------------------------------------
            # 3. 获取播放列表
            # ----------------------------------------------------------
            print("\n--- 3. 获取播放列表 ---")
            try:
                data = await device.get_play_list()
                play_list = data["play_list"]
                print(f"  共 {len(play_list)} 个播放项:")
                for i, item in enumerate(play_list):
                    text = item.get("text") or "(图片)"
                    print(f"    [{i}] {text} (停留 {item['duration']}s)")
            except DeviceOperationError as e:
                print(f"  获取失败: {e}")

            # ----------------------------------------------------------
            # 4. 设置亮度
            # ----------------------------------------------------------
            print("\n--- 4. 设置亮度为 25 ---")
            try:
                await device.set_brightness(brightness=25)
                print("  设置成功")
            except DeviceOperationError as e:
                print(f"  设置失败: {e}")

            # ----------------------------------------------------------
            # 5. 上传播放列表文件
            # ----------------------------------------------------------
            print("\n--- 5. 上传播放列表文件 ---")
            content = "[PLAYLIST]\r\nITEM_NO=001\r\nITEM000=10,0,0,0,0,\\C000000\\Fs2424\\T255000000000\\W安全第一"
            try:
                await device.upload_file(content=content, file_name="play.lst")
                print("  上传成功")
            except DeviceOperationError as e:
                print(f"  上传失败: {e}")

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
