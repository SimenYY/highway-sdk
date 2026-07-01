"""诺瓦协议综合测试。

基于 sdk-v2.x.x 分支 factory.py 注释中的示例报文验证帧序列化的正确性。

注：Nova Frame.from_bytes 存在预存的解析问题（不影响实际设备操作，因为设备方法直接构造响应帧），
因此本测试主要验证序列化正确性。
"""

import struct

import pytest

from highway_sdk.core.exceptions import DeviceOperationError
from highway_sdk.vendors.vms.nova.codec import NovaCodec
from highway_sdk.vendors.vms.nova.spec import ENCODING, Frame, What


class TestNovaFrameSerialization:
    """测试帧序列化 - 验证在相同参数下生成一致的发送报文。"""

    def test_get_play_item_request_serialization(self):
        """验证获取播放项请求帧的序列化。

        sdk-v2.x.x factory.py 实际日志：
        上位机发送：AA FF FF 2D CC EE 0A
        注：0xAA 是起始符需转义，CRC 中包含 0xAA 被转义为 0xEE 0x0A
        """
        frame = Frame(what=What.GET_PLAY_ITEM_REQ)
        serialized = bytes(frame)
        expected = bytes.fromhex("aaffff2dccee0a")
        assert serialized == expected, f"Expected {expected.hex(' ')}, got {serialized.hex(' ')}"

    def test_get_play_list_request_serialization(self):
        """验证获取播放列表请求帧的序列化。

        sdk-v2.x.x factory.py 实际日志：
        上位机发送：AA FF FF 3A CC 77 D2
        """
        frame = Frame(what=What.GET_PLAY_LIST_REQ)
        serialized = bytes(frame)
        expected = bytes.fromhex("aaffff3acc77d2")
        assert serialized == expected, f"Expected {expected.hex(' ')}, got {serialized.hex(' ')}"

    def test_send_file_name_request_serialization(self):
        """验证发送文件名请求帧的序列化。

        sdk-v2.x.x factory.py 实际日志：
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

        sdk-v2.x.x factory.py 实际日志：
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

        sdk-v2.x.x factory.py 实际日志：
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
        """验证发送文件名成功响应解码。"""
        tags = NovaCodec.decode_send_file_name(b"\x01")
        assert tags is not None

    def test_decode_send_file_name_failure(self):
        """验证发送文件名失败响应解码。"""
        with pytest.raises(DeviceOperationError):
            NovaCodec.decode_send_file_name(b"\x00")

    def test_decode_select_play_list_success(self):
        """验证指定播放列表成功响应解码。"""
        tags = NovaCodec.decode_select_play_list(b"\x01")
        assert tags is not None

    def test_decode_select_play_list_failure(self):
        """验证指定播放列表失败响应解码。"""
        with pytest.raises(DeviceOperationError):
            NovaCodec.decode_select_play_list(b"\x00")

    def test_decode_send_file_content_success(self):
        """验证发送文件内容成功响应解码。"""
        # 数据域: block_num(2B) + status(1B=0x01成功)
        tags = NovaCodec.decode_send_file_content(b"\x01\x00\x01")
        assert tags is not None

    def test_decode_send_file_content_failure(self):
        """验证发送文件内容失败响应解码。"""
        with pytest.raises(DeviceOperationError):
            NovaCodec.decode_send_file_content(b"\x01\x00\x00")
