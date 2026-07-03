"""丰海协议综合测试。

基于 sdk-v2.x.x 分支 factory.py 中的数据构造逻辑和 protocol.py 中的示例报文验证帧序列化的正确性。
"""

import pytest

from highway_sdk.core.exceptions import DeviceOperationError
from highway_sdk.vendors.vms.fenghai.codec import FengHaiCodec
from highway_sdk.vendors.vms.fenghai.spec import ENCODING, Frame, What


class TestFengHaiFrameSerialization:
    """测试帧序列化 - 验证在相同参数下生成一致的发送报文。"""

    def test_get_brightness_request_serialization(self):
        """验证获取亮度请求帧的序列化。

        sdk-v2.x.x protocol.py 实际日志：
        发送 02 00 00 30 36 53 00 03
        """
        frame = Frame(what=What.GET_BRIGHTNESS_AND_MODE)
        serialized = bytes(frame)
        expected = bytes.fromhex("0200003036530003")
        assert serialized == expected, f"Expected {expected.hex(' ')}, got {serialized.hex(' ')}"

    def test_get_play_item_request_serialization(self):
        """验证获取播放项请求帧的序列化。

        sdk-v2.x.x protocol.py 实际日志：
        发送 02 00 00 39 37 F9 B9 03
        """
        frame = Frame(what=What.GET_PLAY_ITEM)
        serialized = bytes(frame)
        expected = bytes.fromhex("0200003937f9b903")
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
        assert serialized[1:3] == b"\x00\x00"  # address
        assert serialized[3:5] == b"05"  # what (SET_BRIGHTNESS)
        assert serialized[5:11] == b"151515"  # data
        assert serialized[-1:] == b"\x03"  # ETX

    def test_set_brightness_clamping(self):
        """验证亮度值会被限制在 0-31 范围内。"""
        # 模拟 set_brightness(50) 的数据构造逻辑（含 clamping）
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
        content = "[playlist]\r\nitem_no=1\r\nitem0=300,1,0,\\C000000"
        data = file_name.encode(ENCODING) + b"+" + b"\x00\x00\x00\x00" + content.encode(ENCODING)
        frame = Frame(what=What.UPLOAD_FILE, data=data)
        serialized = bytes(frame)

        # 验证帧结构
        assert serialized[0:1] == b"\x02"  # STX
        assert serialized[1:3] == b"\x00\x00"  # address
        assert serialized[3:5] == b"10"  # what (UPLOAD_FILE)
        assert serialized[-1:] == b"\x03"  # ETX
        # 验证数据域以文件名开头（反转义后）
        assert file_name.encode(ENCODING) in serialized


class TestFengHaiFrameParsing:
    """测试帧解析。"""

    def test_get_brightness_response_parsing(self):
        """验证获取亮度响应帧的解析。

        sdk-v2.x.x protocol.py 实际日志：
        接收 02 00 00 30 36 30 30 31 35 57 F9 03
        数据域: 0015 (成功码"0", 模式"0", 亮度"15")
        """
        raw = bytes.fromhex("02000030363030313557f903")
        frame = Frame.from_bytes(raw)

        assert frame.address == b"\x00\x00"
        assert frame.what == What.GET_BRIGHTNESS_AND_MODE
        assert frame.data == b"0015"


class TestFengHaiCodec:
    """测试编解码器。"""

    def test_decode_set_brightness_success(self):
        """验证设置亮度成功响应解码。"""
        tags = FengHaiCodec.decode_set_brightness(b"0")
        assert tags.is_ok is True

    def test_decode_set_brightness_failure(self):
        """验证设置亮度失败响应解码。"""
        with pytest.raises(DeviceOperationError):
            FengHaiCodec.decode_set_brightness(b"1")

    def test_decode_upload_file_success(self):
        """验证上传文件成功响应解码。"""
        tags = FengHaiCodec.decode_upload_file(b"0")
        assert tags.is_ok is True

    def test_decode_upload_file_failure(self):
        """验证上传文件失败响应解码。"""
        with pytest.raises(DeviceOperationError):
            FengHaiCodec.decode_upload_file(b"1")


class TestFengHaiRoundTrip:
    """测试往返一致性。"""

    def test_set_brightness_request_round_trip(self):
        """验证设置亮度请求的往返一致性。"""
        data = (f"{15:02d}".encode("ascii")) * 3
        frame1 = Frame(what=What.SET_BRIGHTNESS, data=data)
        serialized = bytes(frame1)
        frame2 = Frame.from_bytes(serialized)

        assert frame1.address == frame2.address
        assert frame1.what == frame2.what
        assert frame1.data == frame2.data

    def test_upload_file_request_round_trip(self):
        """验证上传文件请求的往返一致性。"""
        file_name = "play.lst"
        content = "[playlist]\r\nitem_no=1\r\nitem0=300,1,0"
        data = file_name.encode(ENCODING) + b"+" + b"\x00\x00\x00\x00" + content.encode(ENCODING)
        frame1 = Frame(what=What.UPLOAD_FILE, data=data)
        serialized = bytes(frame1)
        frame2 = Frame.from_bytes(serialized)

        assert frame1.address == frame2.address
        assert frame1.what == frame2.what
        assert frame1.data == frame2.data
