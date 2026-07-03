"""显科（XianKe）CMS 设备使用示例。

显科 CMS 协议特点：
- 帧结构：起始符 + 指令 + 数据 + CRC16 + 结束符
- 编码：使用 GBK 编码
- 播放列表：通过 upload_file 上传 .xkl 文件，通过 select_play_list 选择播放

运行方式：
    poetry run python examples/demo_xianke.py
"""

import asyncio

from highway_sdk import XianKeDevice
from highway_sdk.core.exceptions import (
    ConnectionLostError,
    ConnectionTimeoutError,
    ResponseTimeoutError,
)


async def main():
    """显科 CMS 设备完整使用示例。"""
    print("=" * 60)
    print("显科（XianKe）CMS 设备示例")
    print("=" * 60)

    host = "127.0.0.1"
    port = 9004

    try:
        async with await XianKeDevice.connect(host, port, timeout=3.0) as device:
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
                print(f"  原始文本: {data['orig_play_item']}")
                if item:
                    print(f"  文本: {item['text']}")
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
            # 4. 上传播放列表文件
            # ----------------------------------------------------------
            print("\n--- 4. 上传播放列表文件 ---")
            content = "[LIST]\r\nItemCount=1\r\nItem00=10,0,0,0,0,\\F S24\\T255000000000\\U前方限速 减速慢行"
            response = await device.upload_file(content=content, file_name="list\\000.xkl")
            if response.status == "success":
                print("  上传成功")
            else:
                print(f"  上传失败: {response.error_msg}")

            # ----------------------------------------------------------
            # 5. 选择播放列表进行播放
            # ----------------------------------------------------------
            print("\n--- 5. 选择播放列表 000.xkl 播放 ---")
            response = await device.select_play_list(file_name="000.xkl")
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
