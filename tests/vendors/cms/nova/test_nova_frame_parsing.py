"""诺瓦 Frame.from_bytes 解析测试。

基于诺瓦交通协议标准版 V3.11.5 验证 Frame.from_bytes 的解析正确性。

注：之前测试文件注释提到 "Nova Frame.from_bytes 存在预存的解析问题"，
本测试通过 4 个协议标准请求报文往返验证 from_bytes 实际可用。
覆盖对抗性审查发现的问题 12（start/end 校验缺失，CRC 间接保护）和
问题 27（from_bytes 路径零覆盖）。
"""

import pytest

from highway_sdk.core.exceptions import CrcValidationError
from highway_sdk.vendors.cms.nova.spec import Frame, What


class TestNovaFrameFromBytesStandardPackets:
    """验证 Frame.from_bytes 解析协议标准请求报文。"""

    @pytest.mark.parametrize(
        "hex_str, expected_what, expected_address, expected_data",
        [
            # GET_PLAY_ITEM_REQ
            ("AA FF FF 2D CC EE 0A", What.GET_PLAY_ITEM_REQ, b"\xff\xff", b""),
            # GET_PLAY_LIST_REQ
            ("AA FF FF 3A CC 77 D2", What.GET_PLAY_LIST_REQ, b"\xff\xff", b""),
            # SEND_FILE_NAME_REQ (含数据域)
            (
                "AA FF FF 11 FF FF 70 6C 61 79 30 30 31 2E 6C 73 74 CC 5A 9B",
                What.SEND_FILE_NAME_REQ,
                b"\xff\xff",
                b"\xff\xffplay001.lst",
            ),
            # SELECT_PLAY_LIST_REQ (含数据域)
            (
                "AA FF FF 1B 01 CC BF 28",
                What.SELECT_PLAY_LIST_REQ,
                b"\xff\xff",
                b"\x01",
            ),
        ],
        ids=["get_play_item_req", "get_play_list_req", "send_file_name_req", "select_play_list_req"],
    )
    def test_from_bytes_standard_request(self, hex_str, expected_what, expected_address, expected_data):
        """验证 from_bytes 解析协议标准请求报文。"""
        raw = bytes.fromhex(hex_str.replace(" ", ""))
        frame = Frame.from_bytes(raw)

        assert frame.what == expected_what
        assert frame.address == expected_address
        assert frame.data == expected_data


class TestNovaFrameFromBytesRoundTrip:
    """验证 Frame.from_bytes(bytes(frame)) == bytes(frame)（往返一致）。"""

    @pytest.mark.parametrize(
        "frame_kwargs",
        [
            {"what": What.GET_PLAY_ITEM_REQ},
            {"what": What.GET_PLAY_LIST_REQ},
            {"what": What.GET_DEVICE_STATUS_REQ},
            {"what": What.GET_SCREENSHOT_REQ},
            {"what": What.GET_SCREEN_SIZE_REQ},
            {"what": What.GET_SCREEN_STATUS_REQ},
        ],
    )
    def test_round_trip_no_data(self, frame_kwargs):
        """验证无数据帧的往返一致。"""
        frame = Frame(**frame_kwargs)
        raw = bytes(frame)
        parsed = Frame.from_bytes(raw)
        assert bytes(parsed) == raw
        assert parsed.what == frame.what
        assert parsed.address == frame.address
        assert parsed.data == frame.data

    def test_round_trip_with_data(self):
        """验证含数据帧的往返一致（含转义）。"""
        # SELECT_PLAY_LIST_REQ with playlist_id=1
        import struct

        data = struct.pack(">B", 1)
        frame = Frame(what=What.SELECT_PLAY_LIST_REQ, data=data)
        raw = bytes(frame)
        parsed = Frame.from_bytes(raw)
        assert bytes(parsed) == raw
        assert parsed.data == data


class TestNovaFrameFromBytesErrorPaths:
    """验证 Frame.from_bytes 错误路径（覆盖对抗性审查发现的问题 12）。"""

    def test_invalid_start_with_valid_crc_raises_crc_error(self):
        """验证 start 字节错误时通过 CRC 间接检测。

        对抗性审查问题 12 担心 start 不校验，但实际 CRC 计算包含 start 字节，
        所以错误的 start 会导致 CRC 不匹配。
        """
        # start=0x00 而非 0xAA，CRC 不匹配
        bad_msg = bytes.fromhex("00 FF FF 2D CC EE 0A")
        with pytest.raises(CrcValidationError):
            Frame.from_bytes(bad_msg)

    def test_unknown_what_raises_valueerror_unwrapped(self):
        """验证未知 what 抛出 ValueError（未被包装为 HighwaySDKError）。

        对抗性审查问题 12：这是已知缺陷，本测试用于守护该问题被发现。
        如果未来修复（包装为 FrameValidationError），此测试需相应更新。
        """
        # 构造 what=0x99 的报文，CRC 用同一帧算
        # 注意：Nova CRC 计算包含 start + address + what + data + end
        # 这里 what 不在 What 枚举中
        payload = b"\xaa\xff\xff\x99\xcc"
        crc = Frame.calc_crc(payload)
        unknown_msg = payload + crc

        with pytest.raises(ValueError, match="is not a valid What"):
            Frame.from_bytes(unknown_msg)

    def test_crc_mismatch_raises_crc_error(self):
        """验证 CRC 不匹配时抛 CrcValidationError。"""
        # 故意破坏 CRC
        raw = bytes.fromhex("AA FF FF 2D CC EE 0B")  # CRC 末字节从 0A 改为 0B
        with pytest.raises(CrcValidationError):
            Frame.from_bytes(raw)
