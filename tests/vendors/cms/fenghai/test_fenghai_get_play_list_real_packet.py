"""丰海 DOWNLOAD_FILE (get_play_list) 真实报文测试。

基于用户提供的真实设备通信日志验证帧解析与解码器的正确性。

报文来源：实际设备通信日志（2026-07-06 用户提供）
"""

import pytest

from highway_sdk.vendors.cms.fenghai.codec import FengHaiCodec
from highway_sdk.vendors.cms.fenghai.spec import Frame, What


class TestFengHaiRealPacketGetPlayList:
    """测试 DOWNLOAD_FILE (get_play_list) 真实报文解析。

    FengHai DOWNLOAD_FILE 请求格式：file_name + "+" + "0000" + (无 content)
    FengHai DOWNLOAD_FILE 响应格式：success_code(1B="0") + file_name + "+" + "0000" + INI 内容
    """

    # 用户提供的真实报文
    SEND_HEX = "02 00 00 30 39 70 6C 61 79 2E 6C 73 74 2B 00 00 00 00 A3 44 03"
    RECV_HEX = (
        "02 00 00 30 39 30 70 6C 61 79 2E 6C 73 74 2B 00 00 00 00 "
        "5B 70 6C 61 79 6C 69 73 74 5D 0D 0A 69 74 65 6D 5F 6E 6F 3D 31 0D 0A "
        "69 74 65 6D 30 3D 31 30 30 30 2C 31 2C 30 2C 5C 43 30 30 30 30 30 37 "
        "5C 66 66 31 36 31 36 5C 63 32 35 35 30 30 30 30 30 30 30 30 30 "
        "CB ED B5 C0 CA A9 B9 A4 D0 A1 D0 C4 0A BC DD CA BB 0D 0A "
        "60 90 03"
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
        """验证发送帧 what=DOWNLOAD_FILE。"""
        assert send_frame.what == What.DOWNLOAD_FILE

    def test_send_frame_address(self, send_frame):
        """验证发送帧地址。"""
        assert send_frame.address == b"\x00\x00"

    def test_send_frame_data_format(self, send_frame):
        """验证发送帧 data 格式：file_name + "+" + "0000"。

        data = "play.lst" + "+" + "\\x00\\x00\\x00\\x00"
        - file_name = "play.lst" (8 字节)
        - "+" 分隔符 (1 字节)
        - "0000" 尾部固定 4 字节 (但此处是 \\x00 二进制零)
        """
        data = send_frame.data
        assert data == b"play.lst+\x00\x00\x00\x00"
        assert data.startswith(b"play.lst+")

    def test_recv_frame_what(self, recv_frame):
        """验证接收帧 what=DOWNLOAD_FILE。"""
        assert recv_frame.what == What.DOWNLOAD_FILE

    def test_recv_frame_address(self, recv_frame):
        """验证接收帧地址。"""
        assert recv_frame.address == b"\x00\x00"

    def test_recv_frame_data_success_code(self, recv_frame):
        """验证响应 data[0]="0" (ResultCode.SUCCESS)。"""
        assert recv_frame.data[0:1] == b"0"  # ASCII "0" = 0x30

    def test_recv_frame_data_header(self, recv_frame):
        """验证响应 data 头部包含文件名信息。

        data 布局：success_code(1B="0") + file_name + "+" + "0000" + INI 内容
        - data[0] = "0" (success)
        - data[1:9] = "play.lst" (file_name)
        - data[9] = "+" (分隔符)
        - data[10:14] = "\\x00\\x00\\x00\\x00" (固定 4 字节)
        - data[14:] = INI 内容 "[playlist]\\r\\n..."
        """
        data = recv_frame.data
        assert data[0:1] == b"0"
        assert data[1:9] == b"play.lst"
        assert data[9:10] == b"+"
        assert data[10:14] == b"\x00\x00\x00\x00"
        # INI 内容应以 "[playlist]" 开头
        ini_content = data[14:]
        assert ini_content.startswith(b"[playlist]")

    def test_decode_download_file(self, recv_frame):
        """验证 decode_download_file 解析真实响应数据。

        期望解析结果（parse_media 解析转义码后）：
        - 1 个 window（无 nwindows 字段，走 else 分支）
        - window 中 1 个 item（item_no=1）
        - item0 字段：
          - duration=10 (int("1000") * 0.01 = 10)
          - screen_in_mode=1
          - play_speed=0
          - font="f", font_size=1616 (从 \\ff1616 解析)
          - font_color="255000000000" (从 \\c255000000000 解析)
          - text="隧道施工小心\\n驾驶" (解析转义码后的剩余文本)
          - media=完整原始 play_item 字符串
        """
        result = FengHaiCodec.decode_download_file(recv_frame.data)

        assert "windows" in result
        assert len(result["windows"]) == 1
        window = result["windows"][0]
        assert len(window["items"]) == 1

        item = window["items"][0]
        assert item["duration"] == 10
        assert item["screen_in_mode"] == 1
        assert item["play_speed"] == 0
        # parse_media 解析出的结构化字段
        assert item["font"] == "f"
        assert item["font_size"] == 1616
        assert item["font_color"] == "255000000000"
        # text 是解析转义码后的剩余文本（\\n 是字面字符串，由 _parse_play_list 转义）
        assert "隧道施工" in item["text"]
        assert "\\n" in item["text"]
        # media 是完整原始 play_item（含 duration,screen_in_mode 等前缀）
        assert "1000,1,0," in item["media"]
        assert "\\C000007" in item["media"]

    def test_decode_via_codec_dispatch(self, recv_frame):
        """验证通过 codec.decode(frame) 统一分发能正确路由到 decode_download_file。"""
        result = FengHaiCodec.decode(recv_frame)
        assert len(result["windows"]) == 1
        assert len(result["windows"][0]["items"]) == 1


class TestFengHaiGetPlayListRoundTrip:
    """真实报文往返一致性。"""

    def test_send_frame_round_trip(self):
        """验证发送报文往返一致。"""
        raw = bytes.fromhex(TestFengHaiRealPacketGetPlayList.SEND_HEX.replace(" ", ""))
        frame = Frame.from_bytes(raw)
        assert bytes(frame) == raw

    def test_recv_frame_round_trip(self):
        """验证接收报文往返一致。"""
        raw = bytes.fromhex(TestFengHaiRealPacketGetPlayList.RECV_HEX.replace(" ", ""))
        frame = Frame.from_bytes(raw)
        assert bytes(frame) == raw
