"""三思（SanSi）CMS 设备使用示例。

三思 CMS 协议特点：
- 帧结构：起始符 + 指令 + 数据 + CRC16 + 结束符（响应帧无 what 字段）
- 亮度调节：0-31 范围
- 播放列表：通过 upload_file 上传 .lst 文件

运行方式：
    poetry run python examples/demo_sansi.py
"""

import asyncio

from highway_sdk import SanSiDevice
from highway_sdk.core.exceptions import (
    ConnectionLostError,
    ConnectionTimeoutError,
    ResponseTimeoutError,
)


async def main():
    """三思 CMS 设备完整使用示例。"""
    print("=" * 60)
    print("三思（SanSi）CMS 设备示例")
    print("=" * 60)

    host = "127.0.0.1"
    port = 9003

    try:
        async with await SanSiDevice.connect(host, port, timeout=3.0) as device:
            print(f"\n[已连接] {device.__class__.__name__} @ {host}:{port}")

            # ----------------------------------------------------------
            # 1. 获取亮度信息
            # ----------------------------------------------------------
            print("\n--- 1. 获取亮度信息 ---")
            response = await device.get_brightness()
            if response.status == "success" and response.data is not None:
                data = response.data
                print(f"  亮度值: {data['brightness']}%")
                print(f"  控制模式: {data['brightness_mode']}")
                print(f"  采集时间: {data['timestamp']}")
            else:
                print(f"  获取失败: {response.error_msg}")

            # ----------------------------------------------------------
            # 2. 获取当前播放项
            # ----------------------------------------------------------
            print("\n--- 2. 获取当前播放项 ---")
            response = await device.get_play_item()
            if response.status == "success" and response.data is not None:
                data = response.data
                item = data["play_item"]
                print(f"  原始格式: {data['orig_play_item']}")
                if item:
                    print(f"  序号: {item['index']}")
                    print(f"  文本: {item['text']}")
                    print(f"  字体: {item['font']} (大小 {item['font_size']})")
                    print(f"  颜色: {item['font_color']}")
                    print(f"  图片: {item['image_name']}")
                    print(f"  停留时间: {item['duration']} 秒")
            else:
                print(f"  获取失败: {response.error_msg}")

            # ----------------------------------------------------------
            # 3. 获取播放列表
            # ----------------------------------------------------------
            print("\n--- 3. 获取播放列表 ---")
            response = await device.get_play_list()
            if response.status == "success" and response.data is not None:
                data = response.data
                play_list = data["play_list"]
                print(f"  共 {len(play_list)} 个播放项:")
                for i, item in enumerate(play_list):
                    text = item.get("text") or "(图片)"
                    print(f"    [{i}] {text} (停留 {item['duration']}s)")
            else:
                print(f"  获取失败: {response.error_msg}")

            # ----------------------------------------------------------
            # 4. 设置亮度
            # ----------------------------------------------------------
            print("\n--- 4. 设置亮度为 18 ---")
            response = await device.set_brightness(brightness=18)
            if response.status == "success":
                print("  设置成功")
            else:
                print(f"  设置失败: {response.error_msg}")

            # ----------------------------------------------------------
            # 5. 上传播放列表文件
            # ----------------------------------------------------------
            print("\n--- 5. 上传播放列表文件 ---")
            content = (
                "[playlist]\r\n"
                "nwindows=1\r\n"
                "windows0_x=0\r\n"
                "windows0_y=0\r\n"
                "windows0_w=128\r\n"
                "windows0_h=64\r\n"
                "windows0_item_no=1\r\n"
                "windows0_item0=100,0,0,0,0,\\C000000\\Fs3232\\T255000000000\\W注意行车安全"
            )
            response = await device.upload_file(content=content, file_name="play.lst")
            if response.status == "success":
                print("  上传成功")
            else:
                print(f"  上传失败: {response.error_msg}")

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
