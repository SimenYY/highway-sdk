"""电明（DianMing）CMS 设备使用示例。

电明 CMS 协议特点：
- 帧结构：STX + 目的地址 + 源地址 + 指令 + 数据 + CRC16 + ETX
- 亮度调节：支持 0-31 手动调节，或自动模式（FFFFFF）
- 播放列表：使用 INI 格式（[PLAYLIST] / ITEM_NO= / ITEM000=）

运行方式：
    poetry run python examples/demo_dianming.py
"""

import asyncio

from highway_sdk import DianMingDevice
from highway_sdk.core.exceptions import (
    ConnectionLostError,
    ConnectionTimeoutError,
    ResponseTimeoutError,
)


async def main():  # noqa: C901
    """电明 CMS 设备完整使用示例。"""
    print("=" * 60)
    print("电明（DianMing）CMS 设备示例")
    print("=" * 60)

    # 设备连接参数（请根据实际环境修改）
    host = "127.0.0.1"
    port = 9000

    try:
        async with await DianMingDevice.connect(host, port, timeout=3.0) as device:
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
                print(f"  原始格式: {data['orig_play_item']}")
                if item:
                    print(f"  序号: {item['index']}")
                    print(f"  文本: {item['text']}")
                    print(f"  字体: {item['font']} (大小 {item['font_size']})")
                    print(f"  颜色: {item['font_color']}")
                    print(f"  停留时间: {item['duration']} 秒")
            else:
                print(f"  获取失败: {response.error_msg}")

            # ----------------------------------------------------------
            # 3. 获取播放列表
            # ----------------------------------------------------------
            print("\n--- 3. 获取播放列表 ---")
            response = await device.get_play_list(play_id=0, filename="play00.lst")
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
            # 4. 设置亮度（手动模式）
            # ----------------------------------------------------------
            print("\n--- 4. 设置亮度为 20 ---")
            response = await device.set_brightness(brightness=20)
            if response.status == "success":
                print("  设置成功")
            else:
                print(f"  设置失败: {response.error_msg}")

            # ----------------------------------------------------------
            # 5. 设置亮度（自动模式）
            # ----------------------------------------------------------
            print("\n--- 5. 切换为自动亮度模式 ---")
            response = await device.set_brightness(brightness=None)
            if response.status == "success":
                print("  设置成功")
            else:
                print(f"  设置失败: {response.error_msg}")

            # ----------------------------------------------------------
            # 6. 下发播放列表并立即播放
            # ----------------------------------------------------------
            print("\n--- 6. 下发播放列表 ---")
            # 电明播放列表格式：[PLAYLIST]\r\nITEM_NO=001\r\nITEM000=停留时间,入屏,效果,出屏,速度,媒体内容
            content = (
                "[PLAYLIST]\r\n"
                "ITEM_NO=001\r\n"
                "ITEM000=15,0,0,0,0,\\C000000\\Fs3232\\T255000000000\\K000000000000\\W"
                "前方施工 减速慢行"
            )
            response = await device.set_play_list(content, play_id=0)
            if response.status == "success":
                print("  下发成功")
            else:
                print(f"  下发失败: {response.error_msg}")

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
