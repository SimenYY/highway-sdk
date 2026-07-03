"""诺瓦（Nova）CMS 设备使用示例。

诺瓦 CMS 协议特点：
- 帧结构：起始符 + 指令 + 数据 + CRC16 + 结束符
- 文件传输：分块发送（send_file_name → send_file_content）
- 播放列表：通过 select_play_list 指定 ID 播放

运行方式：
    poetry run python examples/demo_nova.py
"""

import asyncio

from highway_sdk import NovaDevice
from highway_sdk.core.exceptions import (
    ConnectionLostError,
    ConnectionTimeoutError,
    ResponseTimeoutError,
)


async def main():  # noqa: C901
    """诺瓦 CMS 设备完整使用示例。"""
    print("=" * 60)
    print("诺瓦（Nova）CMS 设备示例")
    print("=" * 60)

    host = "127.0.0.1"
    port = 9002

    try:
        async with await NovaDevice.connect(host, port, timeout=3.0) as device:
            print(f"\n[已连接] {device.__class__.__name__} @ {host}:{port}")

            # ----------------------------------------------------------
            # 1. 获取亮度信息
            # ----------------------------------------------------------
            print("\n--- 1. 获取亮度信息 ---")
            response = await device.get_brightness()
            if response.status == "success":
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
            if response.status == "success":
                data = response.data
                item = data["play_item"]
                print(f"  原始文本: {data['orig_play_item']}")
                if item:
                    print(f"  文本: {item['text']}")
                    print(f"  图片: {item['image_name']}")
            else:
                print(f"  获取失败: {response.error_msg}")

            # ----------------------------------------------------------
            # 3. 获取播放列表
            # ----------------------------------------------------------
            print("\n--- 3. 获取播放列表 ---")
            response = await device.get_play_list()
            if response.status == "success":
                data = response.data
                play_list = data["play_list"]
                print(f"  共 {len(play_list)} 个播放项:")
                for i, item in enumerate(play_list):
                    text = item.get("text") or "(图片)"
                    print(f"    [{i}] {text} (停留 {item['duration']}s)")
            else:
                print(f"  获取失败: {response.error_msg}")

            # ----------------------------------------------------------
            # 4. 发送文件名（开始文件传输）
            # ----------------------------------------------------------
            print("\n--- 4. 发送文件名 ---")
            response = await device.send_file_name(file_name="play001.lst", block_size=65535)
            if response.status == "success":
                print("  发送成功")
            else:
                print(f"  发送失败: {response.error_msg}")

            # ----------------------------------------------------------
            # 5. 发送文件内容（分块传输）
            # ----------------------------------------------------------
            print("\n--- 5. 发送文件内容 ---")
            content = "[PLAYLIST]\r\nITEM_NO=001\r\nITEM000=10,0,0,0,0,\\C000000\\Fs2424\\T255000000000\\W注意安全"
            response = await device.send_file_content(content=content, block_num=1)
            if response.status == "success":
                print("  发送成功")
            else:
                print(f"  发送失败: {response.error_msg}")

            # ----------------------------------------------------------
            # 6. 选择播放列表播放
            # ----------------------------------------------------------
            print("\n--- 6. 选择播放列表 1 进行播放 ---")
            response = await device.select_play_list(playlist_id=1)
            if response.status == "success":
                print("  切换成功")
            else:
                print(f"  切换失败: {response.error_msg}")

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
