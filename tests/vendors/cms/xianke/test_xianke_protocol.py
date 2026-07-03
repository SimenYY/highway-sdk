"""显科协议综合测试。

基于 sdk-v2.x.x 分支 protocol.py 注释中的示例报文和 factory.py 的数据构造逻辑验证帧序列化的正确性。
"""

import pytest

from highway_sdk.core.exceptions import DeviceOperationError
from highway_sdk.vendors.cms.xianke.codec import XianKeCodec
from highway_sdk.vendors.cms.xianke.spec import ENCODING, Frame, What


class TestXianKeFrameSerialization:
    """测试帧序列化 - 验证在相同参数下生成一致的发送报文。"""

    def test_get_play_item_request_serialization(self):
        """验证获取播放项请求帧的序列化。

        sdk-v2.x.x protocol.py 实际日志：
        发送 02 32 34 30 30 EB 22 03
        帧格式: STX + what(2B) + address(2B) + CRC(2B) + ETX
        """
        frame = Frame(what=What.GET_PLAY_ITEM)
        serialized = bytes(frame)
        expected = bytes.fromhex("0232343030eb2203")
        assert serialized == expected, f"Expected {expected.hex(' ')}, got {serialized.hex(' ')}"

    def test_get_play_list_name_request_serialization(self):
        """验证获取播放列表名称请求帧的序列化。

        sdk-v2.x.x protocol.py 实际日志：
        发送 02 32 33 30 30 6E B2 03
        """
        frame = Frame(what=What.GET_PLAY_LIST_NAME)
        serialized = bytes(frame)
        expected = bytes.fromhex("02323330306eb203")
        assert serialized == expected, f"Expected {expected.hex(' ')}, got {serialized.hex(' ')}"

    def test_get_brightness_request_serialization(self):
        """验证获取亮度请求帧的序列化。

        sdk-v2.x.x protocol.py 实际日志：
        发送 02 30 35 30 30 31 7A 03
        """
        frame = Frame(what=What.GET_BRIGHTNESS_AND_MODE)
        serialized = bytes(frame)
        expected = bytes.fromhex("0230353030317a03")
        assert serialized == expected, f"Expected {expected.hex(' ')}, got {serialized.hex(' ')}"

    def test_select_play_list_request_serialization(self):
        """验证选择播放列表请求帧的序列化。

        sdk-v2.x.x protocol.py 实际日志：
        发送 02 32 32 30 30 30 30 30 2E 78 6B 6C 7A 93 03
        数据域: "000.xkl"
        """
        file_name = "000.xkl"
        data = file_name.encode(ENCODING)
        frame = Frame(what=What.SELECT_PLAY_LIST, data=data)
        serialized = bytes(frame)
        expected = bytes.fromhex("0232323030303030 2e786b6c7a9303".replace(" ", ""))
        assert serialized == expected, f"Expected {expected.hex(' ')}, got {serialized.hex(' ')}"

    def test_upload_file_request_structure(self):
        """验证上传文件请求帧的结构。

        数据构造（参考 sdk-v2.x.x factory.py）：
        data = b"10" + len(file_name).rjust(3, "0") + file_name + b"0000" + content
        file_name = "list\\000.xkl" (长度12)
        """
        file_name = "list\\000.xkl"
        content = "[LIST]\r\nItemCount=001\r\nItem00=2,1,0,1,1,\\C000000"
        data = b"10"
        data += str(len(file_name)).encode("ascii").rjust(3, b"0")
        data += file_name.encode(ENCODING)
        data += b"0000"
        data += content.encode(ENCODING)
        frame = Frame(what=What.UPLOAD_FILE, data=data)
        serialized = bytes(frame)

        # 验证帧结构: STX + what + address + data + CRC + ETX
        assert serialized[0:1] == b"\x02"  # STX
        assert serialized[1:3] == b"20"  # what (UPLOAD_FILE)
        assert serialized[3:5] == b"00"  # address
        assert serialized[-1:] == b"\x03"  # ETX
        # 验证数据域结构: "10" + "012" (长度) + file_name + "0000" + content
        assert b"10012" + file_name.encode(ENCODING) + b"0000" in serialized

    def test_upload_file_request_serialization(self):
        """验证上传文件请求帧完整序列化。

        sdk-v2.x.x protocol.py 实际日志：
        发送 02 32 30 30 30 31 30 30 31 32 6C 69 73 74 5C 30 30 30 2E 78 6B 6C
             30 30 30 30 5B 4C 49 53 54 5D 0D 0A 49 74 65 6D 43 6F 75 6E 74 3D 30
             30 32 0D 0A ... 4D EF 03
        数据域: "10" + "012" + "list\\000.xkl" + "0000" + "[LIST]\\r\\nItemCount=002\\r\\n..."
        """
        file_name = "list\\000.xkl"
        # 使用实际报文中的内容片段（前缀部分）
        content = "[LIST]\r\nItemCount=002\r\n"
        data = b"10"
        data += str(len(file_name)).encode("ascii").rjust(3, b"0")
        data += file_name.encode(ENCODING)
        data += b"0000"
        data += content.encode(ENCODING)
        frame = Frame(what=What.UPLOAD_FILE, data=data)
        serialized = bytes(frame)

        # 验证前缀匹配实际报文
        expected_prefix = bytes.fromhex(
            "02323030303130303132"  # STX + what("20") + address("00") + "10" + "012"
            "6c6973745c3030302e786b6c"  # "list\000.xkl"
            "30303030"  # "0000"
            "5b4c4953545d0d0a"  # "[LIST]\r\n"
            "4974656d436f756e743d3030320d0a"  # "ItemCount=002\r\n"
        )
        assert serialized.startswith(expected_prefix), (
            f"Expected prefix {expected_prefix.hex(' ')}, got {serialized[: len(expected_prefix)].hex(' ')}"
        )


class TestXianKeFrameParsing:
    """测试帧解析。"""

    def test_get_play_item_response_parsing(self):
        """验证获取播放项响应帧的解析。

        sdk-v2.x.x protocol.py 实际日志：
        接收 02 32 34 30 30 01 34 2C 31 2C 30 2C 31 2C 31 2C 5C 43 30 30 30 30 30 30 5C 49 30 30 30 3D B0 03
        """
        raw = bytes.fromhex("023234303001342c312c302c312c312c5c433030303030305c493030303db003")
        frame = Frame.from_bytes(raw)

        assert frame.what == What.GET_PLAY_ITEM
        assert frame.address == b"00"

    def test_select_play_list_response_parsing(self):
        """验证选择播放列表响应帧的解析。

        sdk-v2.x.x protocol.py 实际日志：
        接收 02 32 32 30 30 01 59 FD 03
        数据域: 0x01 (成功)
        """
        raw = bytes.fromhex("02323230300159fd03")
        frame = Frame.from_bytes(raw)

        assert frame.what == What.SELECT_PLAY_LIST
        assert frame.address == b"00"
        assert frame.data == b"\x01"

    def test_upload_file_response_parsing(self):
        """验证上传文件响应帧的解析。

        sdk-v2.x.x protocol.py 实际日志：
        接收 02 32 30 30 30 01 B4 95 03
        数据域: 0x01 (成功)
        """
        raw = bytes.fromhex("0232303030 01b49503".replace(" ", ""))
        frame = Frame.from_bytes(raw)

        assert frame.what == What.UPLOAD_FILE
        assert frame.address == b"00"
        assert frame.data == b"\x01"


class TestXianKeCodec:
    """测试编解码器。"""

    def test_decode_upload_file_success(self):
        """验证上传文件成功响应解码。"""
        result = XianKeCodec.decode_upload_file(b"\x01")
        assert result["is_ok"] is True

    def test_decode_upload_file_failure(self):
        """验证上传文件失败响应解码。"""
        with pytest.raises(DeviceOperationError):
            XianKeCodec.decode_upload_file(b"\x00")

    def test_decode_select_play_list_success(self):
        """验证选择播放列表成功响应解码。"""
        result = XianKeCodec.decode_play_list(b"\x01")
        assert result["is_ok"] is True

    def test_decode_select_play_list_failure(self):
        """验证选择播放列表失败响应解码。"""
        with pytest.raises(DeviceOperationError):
            XianKeCodec.decode_play_list(b"\x00")


class TestXianKeRoundTrip:
    """测试往返一致性。"""

    def test_select_play_list_request_round_trip(self):
        """验证选择播放列表请求的往返一致性。"""
        data = "000.xkl".encode(ENCODING)
        frame1 = Frame(what=What.SELECT_PLAY_LIST, data=data)
        serialized = bytes(frame1)
        frame2 = Frame.from_bytes(serialized)

        assert frame1.address == frame2.address
        assert frame1.what == frame2.what
        assert frame1.data == frame2.data

    def test_upload_file_request_round_trip(self):
        """验证上传文件请求的往返一致性。"""
        file_name = "list\\000.xkl"
        content = "[LIST]\r\nItemCount=001\r\nItem00=2,1,0,1,1"
        data = b"10"
        data += str(len(file_name)).encode("ascii").rjust(3, b"0")
        data += file_name.encode(ENCODING)
        data += b"0000"
        data += content.encode(ENCODING)
        frame1 = Frame(what=What.UPLOAD_FILE, data=data)
        serialized = bytes(frame1)
        frame2 = Frame.from_bytes(serialized)

        assert frame1.address == frame2.address
        assert frame1.what == frame2.what
        assert frame1.data == frame2.data
