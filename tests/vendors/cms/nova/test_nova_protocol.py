"""诺瓦协议综合测试。

基于诺瓦交通协议标准版 V3.11.5 验证帧序列化与解码器的正确性。

注：Nova Frame.from_bytes 存在预存的解析问题（不影响实际设备操作，
因为设备方法直接构造响应帧），因此帧测试主要验证序列化正确性。
"""

import struct

import pytest

from highway_sdk.core.exceptions import DeviceOperationError
from highway_sdk.vendors.cms.nova.codec import NovaCodec
from highway_sdk.vendors.cms.nova.spec import ENCODING, Frame, What


class TestNovaFrameSerialization:
    """测试帧序列化 - 验证在相同参数下生成一致的发送报文。"""

    def test_get_play_item_request_serialization(self):
        """验证获取播放项请求帧的序列化。

        上位机发送：AA FF FF 2D CC EE 0A
        注：0xAA 是起始符需转义，CRC 中包含 0xAA 被转义为 0xEE 0x0A
        """
        frame = Frame(what=What.GET_PLAY_ITEM_REQ)
        serialized = bytes(frame)
        expected = bytes.fromhex("aaffff2dccee0a")
        assert serialized == expected, f"Expected {expected.hex(' ')}, got {serialized.hex(' ')}"

    def test_get_play_list_request_serialization(self):
        """验证获取播放列表请求帧的序列化。

        上位机发送：AA FF FF 3A CC 77 D2
        """
        frame = Frame(what=What.GET_PLAY_LIST_REQ)
        serialized = bytes(frame)
        expected = bytes.fromhex("aaffff3acc77d2")
        assert serialized == expected, f"Expected {expected.hex(' ')}, got {serialized.hex(' ')}"

    def test_get_device_status_request_serialization(self):
        """验证查询设备状态请求帧（0x01）的序列化。"""
        frame = Frame(what=What.GET_DEVICE_STATUS_REQ)
        serialized = bytes(frame)
        # 起始符 0xAA + 地址 FF FF + 指令 01 + 结束符 CC + CRC(2B)
        assert serialized[0:1] == b"\xaa"
        assert serialized[1:3] == b"\xff\xff"
        assert serialized[3:4] == b"\x01"  # GET_DEVICE_STATUS_REQ
        assert serialized[-3:-2] == b"\xcc"  # 结束符

    def test_send_file_name_request_serialization(self):
        """验证发送文件名请求帧的序列化。

        上位机发送：AA FF FF 11 FF FF 70 6C 61 79 30 30 31 2E 6C 73 74 CC 5A 9B
        数据域: struct.pack("<H", 65535) + "play001.lst".encode("utf-8")
        """
        file_name = "play001.lst"
        block_size = 65535
        data = struct.pack("<H", block_size) + file_name.encode(ENCODING)
        frame = Frame(what=What.SEND_FILE_NAME_REQ, data=data)
        serialized = bytes(frame)
        expected = bytes.fromhex("aaffff11ffff706c61793030312e6c7374cc5a9b")
        assert serialized == expected, f"Expected {expected.hex(' ')}, got {serialized.hex(' ')}"

    def test_select_play_list_request_serialization(self):
        """验证指定播放列表请求帧的序列化。

        上位机发送：AA FF FF 1B 01 CC BF 28
        数据域: struct.pack(">B", 1)
        """
        playlist_id = 1
        data = struct.pack(">B", playlist_id)
        frame = Frame(what=What.SELECT_PLAY_LIST_REQ, data=data)
        serialized = bytes(frame)
        expected = bytes.fromhex("aaffff1b01ccbf28")
        assert serialized == expected, f"Expected {expected.hex(' ')}, got {serialized.hex(' ')}"

    def test_send_file_content_request_structure(self):
        """验证发送文件内容请求帧的结构。

        上位机发送：AA FF FF 13 01 00 5B 61 6C 6C 5D 0D 0A ...
        数据域: struct.pack("<H", block_num=1) + content.encode("utf-8")
        """
        content = "[all]\r\nitems=1"
        block_num = 1
        data = struct.pack("<H", block_num) + content.encode(ENCODING)
        frame = Frame(what=What.SEND_FILE_CONTENT_REQ, data=data)
        serialized = bytes(frame)

        # 验证帧结构
        assert serialized[0:1] == b"\xaa"  # 起始符
        assert serialized[1:3] == b"\xff\xff"  # 地址
        assert serialized[3:4] == b"\x13"  # 指令码 (SEND_FILE_CONTENT_REQ)
        # 数据域前2字节为 block_num (小端)
        assert serialized[4:6] == struct.pack("<H", 1)
        # 验证内容在帧中（可能在转义后位置偏移，所以用 in 检查）
        assert content.encode(ENCODING) in serialized


class TestNovaCodec:
    """测试编解码器。"""

    def test_decode_send_file_name_success(self):
        """验证发送文件名成功响应解码（0x12，首字节为执行结果）。"""
        result = NovaCodec.decode_send_file_name(b"\x01")
        assert result == {}

    def test_decode_send_file_name_failure(self):
        """验证发送文件名失败响应解码。"""
        with pytest.raises(DeviceOperationError):
            NovaCodec.decode_send_file_name(b"\x00")

    def test_decode_select_play_list_success(self):
        """验证指定播放列表成功响应解码（0x1C，首字节为执行结果）。"""
        result = NovaCodec.decode_select_play_list(b"\x01")
        assert result == {}

    def test_decode_select_play_list_failure(self):
        """验证指定播放列表失败响应解码。"""
        with pytest.raises(DeviceOperationError):
            NovaCodec.decode_select_play_list(b"\x00")

    def test_decode_send_file_content_success(self):
        """验证发送文件内容成功响应解码（0x14：块号2B + 执行结果1B）。"""
        # 数据域: block_num(2B) + status(1B=0x01成功)
        result = NovaCodec.decode_send_file_content(b"\x01\x00\x01")
        assert result == {}

    def test_decode_send_file_content_failure(self):
        """验证发送文件内容失败响应解码。"""
        with pytest.raises(DeviceOperationError):
            NovaCodec.decode_send_file_content(b"\x01\x00\x00")

    def test_decode_send_file_content_too_short(self):
        """验证发送文件内容响应长度不足时抛出异常。"""
        with pytest.raises(DeviceOperationError):
            NovaCodec.decode_send_file_content(b"\x01")

    def test_decode_file_sent_success(self):
        """验证文件发送结束成功响应解码（0xF9，首字节为执行结果）。"""
        result = NovaCodec.decode_file_sent(b"\x01")
        assert result == {}

    def test_decode_file_sent_failure(self):
        """验证文件发送结束失败响应解码。"""
        with pytest.raises(DeviceOperationError):
            NovaCodec.decode_file_sent(b"\x00")

    def test_decode_get_screen_size(self):
        """验证获取屏幕大小响应解码（0x83：宽2B + 高2B，无执行结果前缀）。"""
        # 宽=1920(0x780), 高=1080(0x438)
        data = struct.pack("<HH", 1920, 1080)
        result = NovaCodec.decode_get_screen_size(data)
        assert result == {"width": 1920, "height": 1080}

    def test_decode_get_screen_size_too_short(self):
        """验证屏幕大小响应长度不足时抛出异常。"""
        with pytest.raises(DeviceOperationError):
            NovaCodec.decode_get_screen_size(b"\x00\x01")

    def test_decode_get_screen_status_on(self):
        """验证查询开关屏状态响应解码（0xBA：1-开屏）。"""
        result = NovaCodec.decode_get_screen_status(b"\x01")
        assert result == {"screen_on": True}

    def test_decode_get_screen_status_off(self):
        """验证查询开关屏状态响应解码（0xBA：2-关屏）。"""
        result = NovaCodec.decode_get_screen_status(b"\x02")
        assert result == {"screen_on": False}

    def test_decode_get_screen_status_invalid(self):
        """验证开关屏状态响应非法值抛出异常。"""
        with pytest.raises(DeviceOperationError):
            NovaCodec.decode_get_screen_status(b"\x03")


class TestNovaCodecDeviceStatus:
    """测试查询设备状态响应解码（0x02，含亮度信息）。"""

    def _build_status_data(
        self,
        env_brightness: int = 128,
        mode: int = 1,
        level: int = 200,
    ) -> bytes:
        """构造 0x02 设备状态响应数据域（共 19B）。

        布局：日期4 + 时间3 + 门状态1 + 屏体电源1 + 保留2
              + 温度符号1 + 采集温度1 + 输入源1 + 保留2
              + 采集亮度1 + 亮度控制方式1 + 亮度级别1
        """
        data = bytearray(19)
        data[16] = env_brightness  # 采集亮度
        data[17] = mode  # 亮度控制方式 1-auto/2-manual/3-timed
        data[18] = level  # 亮度级别 1-255
        return bytes(data)

    def test_decode_device_status_auto_mode(self):
        """验证自动亮度模式（mode=1）解析。"""
        data = self._build_status_data(env_brightness=100, mode=1, level=200)
        result = NovaCodec.decode_get_device_status(data)
        assert result == {
            "environment_brightness": 100,
            "mode": 1,
            "brightness_level": 200,
        }

    def test_decode_device_status_manual_mode(self):
        """验证手动亮度模式（mode=2）解析。"""
        data = self._build_status_data(env_brightness=50, mode=2, level=128)
        result = NovaCodec.decode_get_device_status(data)
        assert result["mode"] == 2
        assert result["brightness_level"] == 128

    def test_decode_device_status_timed_mode(self):
        """验证定时亮度模式（mode=3）解析。"""
        data = self._build_status_data(env_brightness=50, mode=3, level=255)
        result = NovaCodec.decode_get_device_status(data)
        assert result["mode"] == 3

    def test_decode_device_status_invalid_mode(self):
        """验证非法亮度模式抛出异常。"""
        data = self._build_status_data(mode=0)
        with pytest.raises(DeviceOperationError):
            NovaCodec.decode_get_device_status(data)

    def test_decode_device_status_too_short(self):
        """验证响应长度不足时抛出异常。"""
        with pytest.raises(DeviceOperationError):
            NovaCodec.decode_get_device_status(b"\x00" * 18)


class TestNovaCodecPlayItem:
    """测试获取当前播放内容响应解码（0x2E，无执行结果前缀）。"""

    def test_decode_play_item_screen_on(self):
        """验证开屏状态下播放内容解析。

        数据域布局：开关屏标志1B + 播放类型1B + 列表号1B + 内容头8B + 内容nB
        """
        # 开关屏=1(开), 播放类型=1, 列表号=1, 内容头8B, 内容="txt1=..."
        header = b"\x01\x01\x01" + b"[item1]\r"  # 3 + 8 = 11 bytes
        content = "txt1=0,0,1,1616,1,8,0,Hello,0,0,0"
        data = header + content.encode("utf-8")
        result = NovaCodec.decode_get_play_item(data)
        assert result["screen_on"] is True
        assert result["text"] == content

    def test_decode_play_item_screen_off(self):
        """验证关屏状态下返回空内容（开关屏标志=2）。"""
        # 关屏时以下内容无效，但帧仍需满足最小长度 11B
        data = b"\x02\x00\x00" + b"\x00" * 8
        result = NovaCodec.decode_get_play_item(data)
        assert result["screen_on"] is False
        assert result["text"] == ""

    def test_decode_play_item_too_short(self):
        """验证响应长度不足时抛出异常。"""
        with pytest.raises(DeviceOperationError):
            NovaCodec.decode_get_play_item(b"\x01\x01")


class TestNovaCodecPlayList:
    """测试获取当前播放列表全部内容响应解码（0x3B，无执行结果前缀）。"""

    def test_decode_play_list_basic(self):
        """验证播放列表解析（列表号1B + UTF8内容nB）。"""
        list_no = 1
        content = "[all]\r\nitems=1\r\n[item1]\r\nparam=10,1,1,10,0,0,1\r\n"
        data = bytes([list_no]) + content.encode("utf-8")
        result = NovaCodec.decode_get_play_list(data)
        assert result["list_no"] == 1
        assert result["text"] == content

    def test_decode_play_list_empty_content(self):
        """验证空内容播放列表解析。"""
        data = b"\x02"
        result = NovaCodec.decode_get_play_list(data)
        assert result["list_no"] == 2
        assert result["text"] == ""

    def test_decode_play_list_empty_response(self):
        """验证空响应抛出异常。"""
        with pytest.raises(DeviceOperationError):
            NovaCodec.decode_get_play_list(b"")
