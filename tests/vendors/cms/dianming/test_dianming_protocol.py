"""电明协议综合测试。

基于实际设备通信日志验证帧序列化和解析的正确性。
"""

import pytest

from highway_sdk.core.exceptions import CrcValidationError
from highway_sdk.vendors.cms.dianming.codec import DianMingCodec
from highway_sdk.vendors.cms.dianming.spec import Frame, What


class TestDianMingFrameSerialization:
    """测试帧序列化 - 验证在相同参数下生成一致的发送报文。"""

    def test_get_brightness_request_serialization(self):
        """验证获取亮度请求帧的序列化。

        实际日志：
        发送 02 30 31 30 31 32 31 12 CA 03
        """
        frame = Frame(
            dst_addr=b"01",
            src_addr=b"01",
            what=What.GET_BRIGHTNESS_AND_MODE_REQ,
        )

        serialized = bytes(frame)
        expected = bytes.fromhex("0230313031323112ca03")
        assert serialized == expected, f"Expected {expected.hex(' ')}, got {serialized.hex(' ')}"

    def test_get_play_list_request_serialization(self):
        """验证获取播放列表请求帧的序列化。

        实际日志：
        发送 02 30 30 30 31 35 37 30 30 30 30 30 30 30 30 70 6C 61 79 30 30 2E 6C 73 74 BC 91 03
        数据域格式: 8字节偏移量 + 文件名 = "00000000play00.lst"
        """
        offset = b"00000000"
        filename = b"play00.lst"
        data = offset + filename

        frame = Frame(
            dst_addr=b"00",
            src_addr=b"01",
            what=What.GET_PLAY_LIST_REQ,
            data=data,
        )

        serialized = bytes(frame)
        expected = bytes.fromhex("023030303135373030303030303030706c617930302e6c7374bc9103")
        assert serialized == expected, f"Expected {expected.hex(' ')}, got {serialized.hex(' ')}"

    def test_get_play_item_request_serialization(self):
        """验证获取播放项请求帧的序列化。

        实际日志：
        发送 02 30 31 30 31 37 33 CD 7D 03
        """
        frame = Frame(
            dst_addr=b"01",
            src_addr=b"01",
            what=What.GET_PLAY_ITEM_REQ,
        )

        serialized = bytes(frame)
        expected = bytes.fromhex("02303130313733cd7d03")
        assert serialized == expected, f"Expected {expected.hex(' ')}, got {serialized.hex(' ')}"

    def test_set_brightness_auto_request_serialization(self):
        """验证设置自动亮度请求帧的序列化。

        实际日志：
        发送 02 30 31 30 31 32 33 46 46 46 46 46 46 D6 4D 03
        数据域: FFFFFF (自动调节亮度，brightness=None)
        """
        # 模拟 set_brightness(None) 的数据构造逻辑
        data = b"FFFFFF"
        frame = Frame(
            dst_addr=b"01",
            src_addr=b"01",
            what=What.SET_BRIGHTNESS_OR_MODE_REQ,
            data=data,
        )

        serialized = bytes(frame)
        expected = bytes.fromhex("02303130313233464646464646d64d03")
        assert serialized == expected, f"Expected {expected.hex(' ')}, got {serialized.hex(' ')}"

    def test_set_play_list_request_serialization(self):
        """验证下发播放列表请求帧的序列化。

        实际日志：
        发送 02 30 31 30 31 37 31 2B 30 30 30 30 30 30 30 30 70 6C 61 79 30 30 2E
        6C 73 74 5B 50 4C 41 59 4C 49 53 54 5D 0D 0A 49 54 45 4D 5F 4E 4F 3D 30 30
        31 0D 0A 49 54 45 4D 30 30 30 3D 31 35 2C 30 2C 30 2C 30 2C 30 2C 5C 43 30
        30 30 30 30 30 5C 46 73 33 32 33 32 5C 54 32 35 35 30 30 30 30 30 30 30 30
        30 5C 4B 30 30 30 30 30 30 30 30 30 30 30 30 5C 57 C7 B0 B7 BD CA C2 B9 CA
        20 BD BB CD A8 B6 C2 C8 FB D8 D6 03
        数据域: +00000000play00.lst + 播放列表内容
        """
        content = (
            "[PLAYLIST]\r\n"
            "ITEM_NO=001\r\n"
            "ITEM000=15,0,0,0,0,\\C000000\\Fs3232\\T255000000000\\K000000000000\\W"
            "前方事故 交通堵塞"
        )
        # 模拟 set_play_list(content) 的数据构造逻辑
        file_name = "play00.lst"
        data = b"+00000000" + file_name.encode("gbk") + content.encode("gbk")

        frame = Frame(
            dst_addr=b"01",
            src_addr=b"01",
            what=What.SET_PLAY_LIST_AND_PLAY_REQ,
            data=data,
        )

        serialized = bytes(frame)
        expected = bytes.fromhex(
            "023031303137312b3030303030303030706c617930302e6c7374"
            "5b504c41594c4953545d0d0a4954454d5f4e4f3d3030310d0a"
            "4954454d3030303d31352c302c302c302c302c"
            "5c433030303030305c467333323332"
            "5c54323535303030303030303030"
            "5c4b303030303030303030303030"
            "5c57c7b0b7bdcac2b9ca20bdbbcda8b6c2c8fb"
            "d8d603"
        )
        assert serialized == expected, f"Expected {expected.hex(' ')}, got {serialized.hex(' ')}"


class TestDianMingFrameParsing:
    """测试帧解析 - 验证对返回的响应报文能够正确解析。"""

    def test_get_brightness_response_parsing(self):
        """验证获取亮度响应帧的解析。

        实际日志：
        接受 02 30 31 30 31 32 32 46 46 46 46 46 46 49 35 1C 69 03
        数据域: FFFFFFI5 (0x46*6 + 0x49 + 0x35)
        """
        raw = bytes.fromhex("0230313031323246464646464649351c6903")
        frame = Frame.from_bytes(raw)

        assert frame.dst_addr == b"01"
        assert frame.src_addr == b"01"
        assert frame.what == What.GET_BRIGHTNESS_AND_MODE_RESP
        assert frame.data == b"FFFFFFI5"

    def test_get_play_item_response_parsing(self):
        """验证获取播放项响应帧的解析。

        实际日志：
        接受 02 30 31 30 31 37 34 30 30 31 30 30 30 35 30 30 30 30 30 30 30 30 30 5C 43 30 30 30 30 30 30 5C 46 73 33 32 33 32 5C 54 32 35 35 32 35 35 30 30 30 30 30 30 5C 4B 30 30 30 30 30 30 30 30 30 30 30 30 5C 57 B0 B2 C8 AB B5 DA D2 BB 5C 41 D4 A4 B7 C0 CE AA D6 F7 61 81 03
        """
        raw = bytes.fromhex(
            "02303130313734303031303030353030303030303030305c433030303030305c4673333233325c543235353235353030303030305c4b3030303030303030303030305c57b0b2c8abb5dad2bb5c41d4a4b7c0ceaad6f7618103"
        )
        frame = Frame.from_bytes(raw)

        assert frame.dst_addr == b"01"
        assert frame.src_addr == b"01"
        assert frame.what == What.GET_PLAY_ITEM_RESP
        # 数据域长度: 79字节
        assert len(frame.data) == 79

    def test_get_play_list_response_parsing(self):
        """验证获取播放列表响应帧的解析。

        实际日志：
        发送 02 30 30 30 31 35 37 30 30 30 30 30 30 30 30 70 6C 61 79 30 30 2E 6C 73 74 BC 91 03
        接受 02 30 31 30 30 35 38 2B 30 30 30 30 30 30 30 30 70 6C 61 79 30 30 2E 6C 73 74 5B 50 4C 41 59 4C 49 53 54 5D 0D 0A 49 54 45 4D 5F 4E 4F 3D 30 30 31 0D 0A 49 54 45 4D 30 30 30 3D 31 30 30 2C 30 2C 30 2C 30 2C 30 2C 5C 43 30 30 30 30 39 36 5C 46 73 36 34 36 34 5C 54 32 35 35 32 35 35 30 30 30 30 30 30 5C 4B 30 30 30 30 30 30 30 30 30 30 30 30 5C 57 C8 FD C3 C5 C1 AA C2 E7 CF DF B7 FE CE F1 C7 F8 5C 41 D4 DD B2 BB CC E1 B9 A9 BC D3 D3 CD BA CD B3 E4 5C 41 B5 E7 B7 FE CE F1 73 E7 03
        """
        raw = bytes.fromhex(
            "023031303035382b3030303030303030706c617930302e6c73745b504c41594c"
            "4953545d0d0a4954454d5f4e4f3d3030310d0a4954454d3030303d3130302c30"
            "2c302c302c302c5c433030303039365c4673363436345c543235353235353030"
            "303030305c4b3030303030303030303030305c57c8fdc3c5c1aac2e7cfdfb7fe"
            "cef1c7f85c41d4ddb2bbcce1b9a9bcd3d3cdbacdb3e45c41b5e7b7fecef173e7"
            "03"
        )
        frame = Frame.from_bytes(raw)

        assert frame.dst_addr == b"01"
        assert frame.src_addr == b"00"
        assert frame.what == What.GET_PLAY_LIST_RESP

    def test_set_brightness_response_parsing(self):
        """验证设置亮度响应帧的解析。

        实际日志：
        接受 02 30 31 30 31 32 34 31 21 F4 03
        数据域: 1 (成功)
        """
        raw = bytes.fromhex("023031303132343121f403")
        frame = Frame.from_bytes(raw)

        assert frame.dst_addr == b"01"
        assert frame.src_addr == b"01"
        assert frame.what == What.SET_BRIGHTNESS_OR_MODE_RESP
        assert frame.data == b"1"

    def test_set_play_list_response_parsing(self):
        """验证下发播放列表响应帧的解析。

        实际日志：
        接受 02 30 31 30 31 37 32 31 60 A2 03
        数据域: 1 (成功)
        """
        raw = bytes.fromhex("023031303137323160a203")
        frame = Frame.from_bytes(raw)

        assert frame.dst_addr == b"01"
        assert frame.src_addr == b"01"
        assert frame.what == What.SET_PLAY_LIST_AND_PLAY_RESP
        assert frame.data == b"1"


class TestDianMingCodec:
    """测试编解码器 - 验证数据域解析的正确性。"""

    def test_decode_get_brightness(self):
        """验证亮度解码。

        数据域: FFFFFFI5
        - RGB均为"FF"表示自动模式
        - data[6]为模式指示字节(0x49)
        - data[7]为当前亮度值(0x35 = 53)
        """
        data = b"FFFFFFI5"
        result = DianMingCodec.decode_get_brightness(data)

        assert result["mode"] == "auto"
        assert result["brightness"] == 53

    def test_decode_get_play_item(self):
        """验证播放项解码。

        数据域格式:
        [0:3]索引 [3:8]停留时间 [8:10]入屏方式 [10:12]播放效果 [12:14]出屏方式 [14:16]播放速度 [16:]媒体内容
        """
        data = bytes.fromhex(
            "303031303030353030303030303030305c433030303030305c4673333233325c543235353235353030303030305c4b3030303030303030303030305c57b0b2c8abb5dad2bb5c41d4a4b7c0ceaad6f7"
        )
        result = DianMingCodec.decode_get_play_item(data)

        assert result["index"] == "001"
        assert result["duration"] == 50
        assert result["screen_in_mode"] == 0
        assert result["play_effect"] == 0
        assert result["screen_out_mode"] == 0
        assert result["play_speed"] == 0
        assert len(result["media_list"]) > 0

    def test_decode_get_play_list(self):
        """验证播放列表解码。

        数据域格式: ITEM_NO=003\r\nITEM000=50,0,0,0,0,\\C000000\\Fs3232\\T000255000000\\K00000000000000\\W以人为先\\A关闭发声\r\n...
        """
        # 从实际响应中提取的数据域（从ITEM_NO=开始）
        data = (
            b"ITEM_NO=003\r\n"
            b"ITEM000=50,0,0,0,0,\\C000000\\Fs3232\\T000255000000\\K000000000000\\W"
            b"\xd2\xd4\xc8\xcb\xce\xaa\xb1\xbe\\A\xb9\xd8\xb0\xae\xc9\xfa\xc3\xfc\r\n"
            b"ITEM001=50,0,0,0,0,\\C000000\\Fs3232\\T255255000000\\K000000000000\\W"
            b"\xb0\xb2\xc8\xab\xb5\xda\xd2\xbb\\A\xd4\xa4\xb7\xc0\xce\xaa\xd6\xf7\r\n"
            b"ITEM002=50,0,0,0,0,\\C000000\\Fs3232\\T255000000000\\K000000000000\\W"
            b"\xd7\xf1\xd5\xc2\xca\xd8\xb7\xa8\\A\xb0\xb2\xbc\xd1\xca\xbb\r\n"
        )
        result = DianMingCodec.decode_get_play_list(data)

        assert len(result["windows"]) == 1
        assert len(result["windows"][0]["items"]) == 3

        # 验证第一个播放项
        item0 = result["windows"][0]["items"][0]
        assert item0["duration"] == 50
        assert item0["screen_in_mode"] == 0
        assert item0["play_effect"] == 0
        assert item0["screen_out_mode"] == 0
        assert item0["play_speed"] == 0
        assert len(item0["media_list"]) > 0

    def test_decode_set_brightness(self):
        """验证设置亮度响应解码。

        数据域: 1 (成功)
        """
        result = DianMingCodec.decode_set_brightness(b"1")
        assert result["is_ok"] is True

    def test_decode_set_play_list(self):
        """验证下发播放列表响应解码。

        数据域: 1 (成功)
        """
        result = DianMingCodec.decode_set_play_list(b"1")
        assert result["is_ok"] is True


class TestDianMingRoundTrip:
    """测试往返一致性 - 验证序列化和解析的对称性。"""

    def test_brightness_request_round_trip(self):
        """验证亮度请求的往返一致性。"""
        frame1 = Frame(
            dst_addr=b"01",
            src_addr=b"01",
            what=What.GET_BRIGHTNESS_AND_MODE_REQ,
        )

        serialized = bytes(frame1)
        frame2 = Frame.from_bytes(serialized)

        assert frame1.dst_addr == frame2.dst_addr
        assert frame1.src_addr == frame2.src_addr
        assert frame1.what == frame2.what
        assert frame1.data == frame2.data

    def test_play_list_request_round_trip(self):
        """验证播放列表请求的往返一致性。"""
        frame1 = Frame(
            dst_addr=b"00",
            src_addr=b"01",
            what=What.GET_PLAY_LIST_REQ,
            data=b"00000000play00.lst",
        )

        serialized = bytes(frame1)
        frame2 = Frame.from_bytes(serialized)

        assert frame1.dst_addr == frame2.dst_addr
        assert frame1.src_addr == frame2.src_addr
        assert frame1.what == frame2.what
        assert frame1.data == frame2.data

    def test_play_item_request_round_trip(self):
        """验证播放项请求的往返一致性。"""
        frame1 = Frame(
            dst_addr=b"01",
            src_addr=b"01",
            what=What.GET_PLAY_ITEM_REQ,
        )

        serialized = bytes(frame1)
        frame2 = Frame.from_bytes(serialized)

        assert frame1.dst_addr == frame2.dst_addr
        assert frame1.src_addr == frame2.src_addr
        assert frame1.what == frame2.what
        assert frame1.data == frame2.data

    def test_set_brightness_request_round_trip(self):
        """验证设置自动亮度请求的往返一致性。"""
        frame1 = Frame(
            dst_addr=b"01",
            src_addr=b"01",
            what=What.SET_BRIGHTNESS_OR_MODE_REQ,
            data=b"FFFFFF",
        )

        serialized = bytes(frame1)
        frame2 = Frame.from_bytes(serialized)

        assert frame1.dst_addr == frame2.dst_addr
        assert frame1.src_addr == frame2.src_addr
        assert frame1.what == frame2.what
        assert frame1.data == frame2.data

    def test_set_play_list_request_round_trip(self):
        """验证下发播放列表请求的往返一致性。"""
        content = (
            "[PLAYLIST]\r\n"
            "ITEM_NO=001\r\n"
            "ITEM000=15,0,0,0,0,\\C000000\\Fs3232\\T255000000000\\K000000000000\\W"
            "前方事故 交通堵塞"
        )
        data = b"+00000000play00.lst" + content.encode("gbk")
        frame1 = Frame(
            dst_addr=b"01",
            src_addr=b"01",
            what=What.SET_PLAY_LIST_AND_PLAY_REQ,
            data=data,
        )

        serialized = bytes(frame1)
        frame2 = Frame.from_bytes(serialized)

        assert frame1.dst_addr == frame2.dst_addr
        assert frame1.src_addr == frame2.src_addr
        assert frame1.what == frame2.what
        assert frame1.data == frame2.data


class TestDianMingEdgeCases:
    """测试边界情况和异常处理。"""

    def test_invalid_crc_raises_error(self):
        """验证CRC校验失败时抛出异常。"""
        # 构造一个CRC错误的帧
        raw = bytes.fromhex("0230313031323246464646464649351c6903")
        # 修改最后一个字节（CRC的一部分）
        corrupted = raw[:-3] + bytes([0xFF, 0xFF]) + raw[-1:]

        with pytest.raises(CrcValidationError):
            Frame.from_bytes(corrupted)

    def test_empty_data_field(self):
        """验证空数据域的帧处理。"""
        frame = Frame(
            dst_addr=b"01",
            src_addr=b"01",
            what=What.GET_BRIGHTNESS_AND_MODE_REQ,
            data=b"",
        )

        serialized = bytes(frame)
        parsed = Frame.from_bytes(serialized)

        assert parsed.data == b""
