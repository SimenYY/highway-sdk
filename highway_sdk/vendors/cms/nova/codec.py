"""诺瓦厂商编解码器模块。

协议参考：诺瓦交通协议标准版 V3.11.5

注：
1. 部分响应（0x2E/0x3B/0x02/0x83/0xBA）数据域不含"执行结果"前缀，
   直接为业务数据；其余响应（0x08/0x12/0x14/0xF9/0x1C）首字节（或末字节）为执行结果。
"""

import struct

from highway_sdk.core.codec import BaseCodec
from highway_sdk.core.exceptions import DeviceOperationError

from .spec import ResultCode, What


class NovaCodec(BaseCodec):
    """诺瓦CMS编解码器。"""

    @classmethod
    def _is_ok(cls, data: bytes) -> bool:
        """检查返回是否成功（仅用于首字节为执行结果的响应）。"""
        return data.startswith(ResultCode.SUCCESS.value)

    @classmethod
    @BaseCodec.register(What.GET_DEVICE_STATUS_RESP)
    def decode_get_device_status(cls, data: bytes) -> dict:
        """解码查询设备状态响应（0x02）。

        数据域布局（共 19B）：
            日期 4B + 时间 3B + 门状态 1B + 屏体电源 1B + 保留 2B
            + 当前温度符号 1B + 采集温度 1B + 输入源 1B + 保留 2B
            + 采集亮度 1B + 亮度控制方式 1B + 亮度级别 1B

        亮度控制方式：1-自动 / 2-手动 / 3-定时
        亮度级别：1-255（手动级别，非百分比）
        """
        if len(data) < 19:
            raise DeviceOperationError(
                f"设备状态响应数据不完整（{len(data)} 字节，需 19 字节），可能是通信中断或设备协议版本不匹配"
            )
        mode_val = int(data[17])
        if mode_val not in (1, 2, 3):
            raise DeviceOperationError(f"设备返回的亮度控制方式无效（{mode_val}），可能是设备协议版本不匹配或设备故障")
        return {
            "environment_brightness": int(data[16]),  # 采集亮度 0-255
            "mode": mode_val,  # 1-auto, 2-manual, 3-timed
            "brightness_level": int(data[18]),  # 亮度级别 1-255
        }

    @classmethod
    @BaseCodec.register(What.GET_PLAY_ITEM_RESP)
    def decode_get_play_item(cls, data: bytes) -> dict:
        """解码获取当前播放内容响应（0x2E）。

        数据域布局（无执行结果前缀）：
            开关屏标志 1B（1-开屏 / 2-关屏，关屏时以下内容无效）
            播放类型标志 1B（1-列表播放）
            播放列表号 1B
            内容头 8B（"[itemN]\\r\\n"）
            当前播放内容 nB（参见附录一）
        """
        if len(data) < 11:
            raise DeviceOperationError(
                f"播放项响应数据不完整（{len(data)} 字节，需 11 字节），可能是通信中断或设备协议版本不匹配"
            )
        screen_flag = int(data[0])
        if screen_flag == 2:
            # 关屏，无播放内容
            return {"screen_on": False, "text": ""}
        content = data[11:].decode("utf-8", errors="ignore")
        return {"screen_on": screen_flag == 1, "text": content}

    @classmethod
    @BaseCodec.register(What.GET_PLAY_LIST_RESP)
    def decode_get_play_list(cls, data: bytes) -> dict:
        """解码获取当前播放列表全部内容响应（0x3B）。

        数据域布局（无执行结果前缀）：
            当前播放节目的列表编号 1B（0x01 代表 play001.lst）
            当前播放节目的所有内容 N B（UTF8 编码，格式同附录单个 item）
        """
        if len(data) < 1:
            raise DeviceOperationError("播放列表响应为空，可能是设备未配置播放列表或通信故障")
        list_no = int(data[0])
        content = data[1:].decode("utf-8", errors="ignore")
        return {"list_no": list_no, "text": content}

    @classmethod
    @BaseCodec.register(What.SEND_FILE_NAME_RESP)
    def decode_send_file_name(cls, data: bytes) -> dict:
        """解码发送文件名响应（0x12）。

        数据域：执行结果 1B（1-成功 / 0-失败 / 2-文件已存在）。
        """
        if not cls._is_ok(data):
            raise DeviceOperationError("发送文件名失败：设备返回错误响应，可能是文件名无效或设备故障")
        return {}

    @classmethod
    @BaseCodec.register(What.SEND_FILE_CONTENT_RESP)
    def decode_send_file_content(cls, data: bytes) -> dict:
        """解码发送文件内容响应（0x14）。

        数据域：块号 2B + 执行结果 1B（1-成功 / 0-失败）。
        """
        if len(data) < 3:
            raise DeviceOperationError("文件内容响应数据过短，可能是设备返回不完整或通信中断")
        if data[-1:] != ResultCode.SUCCESS.value:
            raise DeviceOperationError("发送文件内容失败：设备返回错误响应，可能是存储空间不足或设备故障")
        return {}

    @classmethod
    @BaseCodec.register(What.FILE_SENT_RESP)
    def decode_file_sent(cls, data: bytes) -> dict:
        """解码文件发送结束响应（0xF9）。

        数据域：执行结果 1B（1-发送成功 / 0-发送失败）。
        """
        if not cls._is_ok(data):
            raise DeviceOperationError("文件发送结束失败：设备返回错误响应，可能是设备故障或通信中断")
        return {}

    @classmethod
    @BaseCodec.register(What.SELECT_PLAY_LIST_RESP)
    def decode_select_play_list(cls, data: bytes) -> dict:
        """解码指定播放列表播放响应（0x1C）。

        数据域：执行结果 1B（1-成功 / 0-失败）。
        """
        if not cls._is_ok(data):
            raise DeviceOperationError("选择播放列表失败：设备返回错误响应，可能是播放列表编号不存在或设备故障")
        return {}

    @classmethod
    @BaseCodec.register(What.GET_SCREEN_SIZE_RESP)
    def decode_get_screen_size(cls, data: bytes) -> dict:
        """解码获取屏幕大小响应（0x83）。

        数据域：显示屏宽 2B + 显示屏高 2B（均低字节在前）。
        """
        if len(data) < 4:
            raise DeviceOperationError("屏幕尺寸响应数据过短，可能是设备返回不完整或通信中断")
        width, height = struct.unpack("<HH", data[:4])
        return {"width": width, "height": height}

    @classmethod
    @BaseCodec.register(What.GET_SCREEN_STATUS_RESP)
    def decode_get_screen_status(cls, data: bytes) -> dict:
        """解码查询开关屏状态响应（0xBA）。

        数据域：执行结果 1B（1-开屏 / 2-关屏）。
        """
        if len(data) < 1:
            raise DeviceOperationError("屏幕状态响应为空，可能是设备故障或通信中断")
        status = int(data[0])
        if status not in (1, 2):
            raise DeviceOperationError(f"设备返回的屏幕状态值无效（{status}），可能是设备协议版本不匹配或设备故障")
        return {"screen_on": status == 1}
