"""显科协议真实报文测试。

基于用户提供的真实设备通信日志验证帧解析与解码器的正确性。

报文来源：实际设备通信日志（2026-07-06 用户提供）
"""

import pytest

from highway_sdk.vendors.cms.xianke.codec import XianKeCodec
from highway_sdk.vendors.cms.xianke.spec import Frame, What


class TestXianKeRealPacketGetPlayList:
    """测试 DOWNLOAD_FILE (get_play_list) 真实报文解析。

    响应格式：success_code(1B) + file_name_len(3B ASCII) + file_name + "0000"(4B) + INI 内容
    """

    # 用户提供的真实报文
    SEND_HEX = "02 32 31 30 30 30 31 32 6C 69 73 74 5C 30 30 30 2E 78 6B 6C 30 30 30 30 3A 87 03"
    RECV_HEX = (
        "02 32 31 30 30 01 30 31 32 6C 69 73 74 5C 30 30 30 2E 78 6B 6C 30 "
        "30 30 30 5B 4C 49 53 54 5D 0D 0A 49 74 65 6D 43 6F 75 6E 74 3D 30 30 "
        "32 0D 0A 49 74 65 6D 30 30 3D 32 2C 31 2C 30 2C 31 2C 31 2C 5C 43 30 30 "
        "30 30 30 30 5C 46 73 33 32 5C 54 32 35 35 30 30 30 30 30 30 30 30 30 "
        "5C 42 30 30 30 30 30 30 30 30 30 30 30 30 5C 55 C9 EE DB DA CF D4 BF C6 BF C6 BC BC D3 D0 CF DE B9 AB CB BE 0D 0A 49 74 65 6D 30 31 3D "
        "32 2C 31 2C 30 2C 31 2C 31 2C 5C 43 30 30 30 30 30 30 5C 46 73 33 32 "
        "5C 54 30 30 30 32 35 35 30 30 30 30 30 30 5C 42 30 30 30 30 30 30 30 "
        "30 30 30 30 30 5C 55 C9 EE DB DA CF D4 BF C6 BF C6 BC BC D3 D0 CF DE "
        "B9 AB CB BE 0D 0A F2 52 03"
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
        assert send_frame.address == b"00"

    def test_send_frame_data_format(self, send_frame):
        """验证发送帧 data 格式：file_name_len(3) + file_name + "0000"。

        data = "012list\\000.xkl0000"
        - "012" = file_name_len = 12
        - "list\\000.xkl" = file_name (12 字节)
        - "0000" = 尾部固定 4 字节
        """
        data = send_frame.data
        assert data[:3] == b"012"
        file_name_len = int(data[:3])
        assert file_name_len == 12
        assert data[3 : 3 + file_name_len] == b"list\\000.xkl"
        assert data[3 + file_name_len : 3 + file_name_len + 4] == b"0000"

    def test_recv_frame_what(self, recv_frame):
        """验证接收帧 what=DOWNLOAD_FILE。"""
        assert recv_frame.what == What.DOWNLOAD_FILE

    def test_recv_frame_address(self, recv_frame):
        """验证接收帧地址。"""
        assert recv_frame.address == b"00"

    def test_recv_frame_data_success_code(self, recv_frame):
        """验证响应 data[0]=0x01 (ResultCode.SUCCESS)。"""
        assert recv_frame.data[0] == 0x01

    def test_recv_frame_data_header(self, recv_frame):
        """验证响应 data 头部包含文件名信息。

        data[1:4] = "012" (file_name_len=12)
        data[4:16] = "list\\000.xkl" (file_name)
        data[16:20] = "0000" (尾部固定 4 字节)
        data[20:] = INI 内容
        """
        data = recv_frame.data
        assert data[1:4] == b"012"
        file_name_len = int(data[1:4])
        assert file_name_len == 12
        assert data[4 : 4 + file_name_len] == b"list\\000.xkl"
        assert data[4 + file_name_len : 4 + file_name_len + 4] == b"0000"
        # INI 内容应以 "[LIST]" 开头
        ini_content = data[4 + file_name_len + 4 :]
        assert ini_content.startswith(b"[LIST]")

    def test_decode_download_file(self, recv_frame):
        """验证 decode_download_file 解析真实响应数据。

        期望解析结果：
        - 1 个 window
        - window 中 2 个 items（ItemCount=002）
        - 每个 item 包含字体、颜色、背景色、文本等字段
        - 文本内容包含 "深圳显科科技有限公司"
        """
        result = XianKeCodec.decode_download_file(recv_frame.data)

        assert "windows" in result
        assert len(result["windows"]) == 1
        window = result["windows"][0]
        assert len(window["items"]) == 2

        item0 = window["items"][0]
        assert item0["duration"] == 2
        assert item0["screen_in_mode"] == 1
        assert item0["play_effect"] == 0
        assert item0["screen_out_mode"] == 1
        assert item0["play_speed"] == 1
        assert item0["font"] == "s"
        assert item0["font_size"] == 32
        assert item0["font_color"] == "255000000000"
        assert item0["background_color"] == "000000000000"
        assert "深圳显科科技有限公司" in item0["text"]

        item1 = window["items"][1]
        assert item1["font_color"] == "000255000000"  # 第二项颜色不同
        assert "深圳显科科技有限公司" in item1["text"]

    def test_decode_via_codec_dispatch(self, recv_frame):
        """验证通过 codec.decode(frame) 统一分发能正确路由到 decode_download_file。"""
        result = XianKeCodec.decode(recv_frame)
        assert len(result["windows"]) == 1
        assert len(result["windows"][0]["items"]) == 2


class TestXianKeRealPacketRoundTrip:
    """真实报文往返一致性。"""

    def test_send_frame_round_trip(self):
        """验证发送报文往返一致。"""
        raw = bytes.fromhex(TestXianKeRealPacketGetPlayList.SEND_HEX.replace(" ", ""))
        frame = Frame.from_bytes(raw)
        assert bytes(frame) == raw

    def test_recv_frame_round_trip(self):
        """验证接收报文往返一致。"""
        raw = bytes.fromhex(TestXianKeRealPacketGetPlayList.RECV_HEX.replace(" ", ""))
        frame = Frame.from_bytes(raw)
        assert bytes(frame) == raw


class TestXianKeDecodeDownloadFileErrorPaths:
    """验证 decode_download_file 错误路径覆盖（修复 bug 时新增的保护）。"""

    def test_decode_download_file_too_short(self):
        """验证响应过短时抛 DeviceOperationError。"""
        from highway_sdk.core.exceptions import DeviceOperationError

        # data 长度 < 8
        with pytest.raises(DeviceOperationError, match="too short"):
            XianKeCodec.decode_download_file(b"\x01" + b"012")

    def test_decode_download_file_invalid_filename_len(self):
        """验证 file_name_len 非数字时抛 DeviceOperationError。"""
        from highway_sdk.core.exceptions import DeviceOperationError

        # data[1:4] = "abc" 非数字
        bad_data = b"\x01" + b"abc" + b"0000" + b"[LIST]\r\n"
        with pytest.raises(DeviceOperationError, match="Invalid file_name_len"):
            XianKeCodec.decode_download_file(bad_data)

    def test_decode_download_file_truncated_header(self):
        """验证文件头被截断时抛 DeviceOperationError。"""
        from highway_sdk.core.exceptions import DeviceOperationError

        # file_name_len=999 但实际只有少量数据
        bad_data = b"\x01" + b"999" + b"short" + b"0000"
        with pytest.raises(DeviceOperationError, match="truncated file header"):
            XianKeCodec.decode_download_file(bad_data)

    def test_decode_download_file_failure_status(self):
        """验证响应失败码时抛 DeviceOperationError。"""
        from highway_sdk.core.exceptions import DeviceOperationError

        # data[0] = 0x00 (FAILED)
        with pytest.raises(DeviceOperationError, match="Failed to download file"):
            XianKeCodec.decode_download_file(b"\x00" + b"012list\\000.xkl0000[LIST]\r\n")
