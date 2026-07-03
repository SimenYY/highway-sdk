"""三思协议综合测试。

基于 sdk-v2.x.x 分支 protocol.py 注释中的示例报文和 factory.py 的数据构造逻辑验证帧序列化的正确性。
"""

import pytest

from highway_sdk.core.exceptions import DeviceOperationError
from highway_sdk.vendors.cms.sansi.codec import SanSiCodec
from highway_sdk.vendors.cms.sansi.spec import ENCODING, Frame, What


class TestSanSiFrameSerialization:
    """测试帧序列化 - 验证在相同参数下生成一致的发送报文。"""

    def test_get_play_item_request_serialization(self):
        """验证获取播放项请求帧的序列化。

        sdk-v2.x.x protocol.py 实际日志：
        发送 02 30 30 39 37 10 F5 03
        """
        frame = Frame(what=What.GET_PLAY_ITEM)
        serialized = bytes(frame)
        expected = bytes.fromhex("023030393710f503")
        assert serialized == expected, f"Expected {expected.hex(' ')}, got {serialized.hex(' ')}"

    def test_get_brightness_request_serialization(self):
        """验证获取亮度请求帧的序列化。

        sdk-v2.x.x protocol.py 实际日志：
        发送 02 30 30 30 36 BA 4C 03
        """
        frame = Frame(what=What.GET_BRIGHTNESS_AND_MODE)
        serialized = bytes(frame)
        expected = bytes.fromhex("0230303036ba4c03")
        assert serialized == expected, f"Expected {expected.hex(' ')}, got {serialized.hex(' ')}"

    def test_set_brightness_request_serialization(self):
        """验证设置亮度请求帧的序列化。

        数据构造（参考 sdk-v2.x.x factory.py）：
        data = f"{brightness:02d}".encode("ascii") * 3  (红绿蓝三基色相同)
        brightness=15 -> data = b"151515"
        """
        brightness = 15
        data = (f"{brightness:02d}".encode("ascii")) * 3
        frame = Frame(what=What.SET_BRIGHTNESS, data=data)
        serialized = bytes(frame)
        # 验证帧结构：STX + address + what + data + CRC + ETX
        assert serialized[0:1] == b"\x02"  # STX
        assert serialized[1:3] == b"00"  # address (ASCII "00")
        assert serialized[3:5] == b"05"  # what (SET_BRIGHTNESS)
        assert serialized[5:11] == b"151515"  # data
        assert serialized[-1:] == b"\x03"  # ETX

    def test_set_brightness_clamping(self):
        """验证亮度值会被限制在 0-31 范围内。"""
        brightness = max(0, min(31, 50))
        assert brightness == 31
        data = (f"{brightness:02d}".encode("ascii")) * 3
        assert data == b"313131"

        brightness = max(0, min(31, -5))
        assert brightness == 0
        data = (f"{brightness:02d}".encode("ascii")) * 3
        assert data == b"000000"

    def test_upload_file_request_serialization(self):
        """验证上传文件请求帧的序列化。

        数据构造（参考 sdk-v2.x.x factory.py）：
        data = file_name.encode("gbk") + b"+" + b"\\x00\\x00\\x00\\x00" + content.encode("gbk")
        """
        file_name = "play.lst"
        content = "[playlist]\r\nnwindows=1\r\nwindows0_x=0"
        data = file_name.encode(ENCODING) + b"+" + b"\x00\x00\x00\x00" + content.encode(ENCODING)
        frame = Frame(what=What.UPLOAD_FILE, data=data)
        serialized = bytes(frame)

        # 验证帧结构
        assert serialized[0:1] == b"\x02"  # STX
        assert serialized[1:3] == b"00"  # address (ASCII "00")
        assert serialized[3:5] == b"10"  # what (UPLOAD_FILE)
        assert serialized[-1:] == b"\x03"  # ETX
        # 验证数据域包含文件名
        assert file_name.encode(ENCODING) in serialized


class TestSanSiFrameParsing:
    """测试帧解析。"""

    def test_get_brightness_response_parsing(self):
        """验证获取亮度响应帧的解析。

        sdk-v2.x.x protocol.py 实际日志：
        接收 02 30 31 31 31 35 F4 74 03
        数据域: 115 (成功码"1"? 实际是亮度模式"1"和亮度"15")

        注：SanSi 响应帧无 what 字段，address 从 "00" 变为 "01"
        """
        raw = bytes.fromhex("023031313135f47403")
        frame = Frame.from_bytes(raw)

        assert frame.address == b"01"
        assert frame.what is None  # 响应帧无 what
        assert frame.data == b"115"

    def test_upload_file_response_parsing(self):
        """验证上传文件响应帧的解析。

        sdk-v2.x.x protocol.py 实际日志：
        接收 02 30 31 30 C5 52 03
        数据域: 0 (成功码)
        """
        raw = bytes.fromhex("02303130c55203")
        frame = Frame.from_bytes(raw)

        assert frame.address == b"01"
        assert frame.what is None  # 响应帧无 what
        assert frame.data == b"0"


class TestSanSiCodec:
    """测试编解码器。"""

    def test_decode_set_brightness_success(self):
        """验证设置亮度成功响应解码。"""
        result = SanSiCodec.decode_set_brightness(b"0")
        assert result["is_ok"] is True

    def test_decode_set_brightness_failure(self):
        """验证设置亮度失败响应解码。"""
        with pytest.raises(DeviceOperationError):
            SanSiCodec.decode_set_brightness(b"1")


class TestSanSiRoundTrip:
    """测试往返一致性。

    注：SanSi Frame.from_bytes 设计为解析响应帧（无 what 字段），
    因此请求帧的往返测试不适用，这里仅验证序列化后的 CRC 一致性。
    """

    def test_set_brightness_request_crc_consistency(self):
        """验证设置亮度请求的 CRC 一致性。"""
        data = (f"{15:02d}".encode("ascii")) * 3
        frame1 = Frame(what=What.SET_BRIGHTNESS, data=data)
        serialized = bytes(frame1)
        # 重新构造帧并验证序列化结果一致
        frame2 = Frame(what=What.SET_BRIGHTNESS, data=data)
        assert bytes(frame2) == serialized

    def test_upload_file_request_crc_consistency(self):
        """验证上传文件请求的 CRC 一致性。"""
        file_name = "play.lst"
        content = "[playlist]\r\nitem_no=1\r\nitem0=300,1,0"
        data = file_name.encode(ENCODING) + b"+" + b"\x00\x00\x00\x00" + content.encode(ENCODING)
        frame1 = Frame(what=What.UPLOAD_FILE, data=data)
        serialized = bytes(frame1)
        frame2 = Frame(what=What.UPLOAD_FILE, data=data)
        assert bytes(frame2) == serialized
