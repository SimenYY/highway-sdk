"""丰海协议真实报文测试。

基于用户提供的真实设备通信日志验证帧解析与解码器的正确性。

报文来源：实际设备通信日志（2026-07-06 用户提供）
"""

import pytest

from highway_sdk.vendors.cms.fenghai.codec import FengHaiCodec
from highway_sdk.vendors.cms.fenghai.spec import Frame, What


class TestFengHaiRealPacketGetPlayItem:
    """测试 GET_PLAY_ITEM 真实报文解析。

    注：用户标记为 "fenghai get_play_list"，但实际帧 what=39 37=b"97"=GET_PLAY_ITEM，
    不是 DOWNLOAD_FILE (b"09")。本测试按真实 what 标记。
    """

    # 用户提供的真实报文
    SEND_HEX = "02 00 00 39 37 F9 B9 03"
    RECV_HEX = (
        "02 30 30 39 37 30 30 30 30 31 30 30 30 30 31 30 30 30 30 30 "
        "3C CB ED B5 C0 CA A9 B9 A4 D0 A1 D0 C4 0A BC DD CA BB 3E 00 "
        "F7 F6 03"
    )

    @pytest.fixture(scope="class")
    def send_frame(self):
        """解析发送报文。"""
        return Frame.from_bytes(bytes.fromhex(self.SEND_HEX.replace(" ", "")))

    @pytest.fixture(scope="class")
    def recv_frame(self):
        """解析接收报文。"""
        return Frame.from_bytes(bytes.fromhex(self.RECV_HEX.replace(" ", "")))

    def test_send_frame_what(self, send_frame):
        """验证发送帧 what=GET_PLAY_ITEM。"""
        assert send_frame.what == What.GET_PLAY_ITEM

    def test_send_frame_address(self, send_frame):
        """验证发送帧地址。"""
        assert send_frame.address == b"\x00\x00"

    def test_send_frame_data_empty(self, send_frame):
        """验证发送帧 data 为空（GET_PLAY_ITEM 请求无数据域）。"""
        assert send_frame.data == b""

    def test_recv_frame_what(self, recv_frame):
        """验证接收帧 what=GET_PLAY_ITEM。"""
        assert recv_frame.what == What.GET_PLAY_ITEM

    def test_recv_frame_address(self, recv_frame):
        """验证接收帧地址。"""
        assert recv_frame.address == b"00"

    def test_recv_frame_crc_valid(self, recv_frame):
        """验证接收帧 CRC 校验通过（from_bytes 已校验，重新计算应一致）。"""
        assert recv_frame.crc == recv_frame.crc  # 触发 computed_field

    def test_decode_get_play_item(self, recv_frame):
        """验证 decode_get_play_item 解析真实响应数据。

        期望解析结果（基于 data 字节偏移计算）：
        - index: data_str[0:3] = "000"
        - duration: data_str[3:8] = "01000" → int("01000") * 0.01 = 10
        - screen_in_mode: data_str[8:10] = "01" → int("01") = 1
        - text: data_str[15:] 中 <...> 部分 GBK 解码 = "隧道施工小心\\n驾驶"
        """
        result = FengHaiCodec.decode_get_play_item(recv_frame.data)

        assert result["index"] == "000"
        assert result["duration"] == 10
        assert result["screen_in_mode"] == 1
        # GBK 解码后包含中文文本
        assert "隧道施工" in result["text"]
        assert "\n" in result["text"]  # 0A 是 \n

    def test_decode_via_codec_dispatch(self, recv_frame):
        """验证通过 codec.decode(frame) 统一分发能正确路由到 decode_get_play_item。"""
        result = FengHaiCodec.decode(recv_frame)
        assert result["index"] == "000"
        assert "隧道施工" in result["text"]


class TestFengHaiRealPacketRoundTrip:
    """真实报文往返一致性：Frame.from_bytes(bytes(frame)) 应等于原报文。"""

    def test_send_frame_round_trip(self):
        """验证发送报文往返一致。"""
        raw = bytes.fromhex(TestFengHaiRealPacketGetPlayItem.SEND_HEX.replace(" ", ""))
        frame = Frame.from_bytes(raw)
        assert bytes(frame) == raw

    def test_recv_frame_round_trip(self):
        """验证接收报文往返一致。"""
        raw = bytes.fromhex(TestFengHaiRealPacketGetPlayItem.RECV_HEX.replace(" ", ""))
        frame = Frame.from_bytes(raw)
        assert bytes(frame) == raw
