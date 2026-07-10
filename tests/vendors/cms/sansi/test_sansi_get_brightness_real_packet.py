"""三思 get_brightness 真实报文测试。

报文来源：sdk-v2.x.x protocol.py 实际日志（GET_BRIGHTNESS_AND_MODE 指令）

SanSi 的 get_brightness 通过 GET_BRIGHTNESS_AND_MODE (b"06") 指令获取，
响应数据域为 3 字节 ASCII：mode(1B) + brightness(2B)。

本测试验证：
1. set_brightness 发送的帧字节与真实设备日志完全一致
2. 设备返回真实响应时，get_brightness 返回 CmsTags 且数据正确
3. 数据域解码结果与真实设备语义一致（mode=1, brightness=48%）
"""

from collections.abc import Sequence

import pytest

from highway_sdk.core.transport import Transport
from highway_sdk.vendors.cms.sansi.device import SanSiCms
from highway_sdk.vendors.cms.sansi.spec import What
from highway_sdk.vendors.cms.tags import CmsTags


class FakeTransport(Transport):
    """模拟传输层：记录发送字节并按序返回预设响应。"""

    def __init__(self, responses: Sequence[bytes]):
        # 不调用 super().__init__ 以避免创建真实 socket
        self._responses = list(responses)
        self._sent_frames: list[bytes] = []
        self._is_connected = True

    @property
    def is_connected(self) -> bool:
        return self._is_connected

    async def connect(self) -> None:
        self._is_connected = True

    async def disconnect(self) -> None:
        self._is_connected = False

    async def request(self, data: bytes, timeout: float | None = None) -> bytes:
        self._sent_frames.append(data)
        if not self._responses:
            raise RuntimeError("No canned response available")
        return self._responses.pop(0)


# sdk-v2.x.x protocol.py 实际日志：
# 发送 02 30 30 30 36 BA 4C 03
# 解析：STX(02) + address("00") + what("06"=GET_BRIGHTNESS_AND_MODE) + CRC(BA4C) + ETX(03)
REAL_SEND_HEX = "0230303036ba4c03"

# sdk-v2.x.x protocol.py 实际日志：
# 接收 02 30 31 31 31 35 F4 74 03
# 解析：STX(02) + address("01") + data("115") + CRC(F474) + ETX(03)
# 数据域语义：mode='1' + brightness='15' (ASCII)
# 解码结果：mode=1, brightness=round(15/31*100)=48
REAL_RECV_HEX = "023031313135f47403"


class TestSanSiGetBrightnessRealPacket:
    """测试 SanSiCms.get_brightness 与真实报文的一致性。"""

    @pytest.mark.asyncio
    async def test_get_brightness_send_frame_matches_real_packet(self):
        """验证 get_brightness 发送的帧字节与真实设备日志完全一致。"""
        transport = FakeTransport(responses=[bytes.fromhex(REAL_RECV_HEX)])
        device = SanSiCms(transport)

        await device.get_brightness()

        # 验证：发送字节与真实报文完全一致
        assert len(transport._sent_frames) == 1
        expected = bytes.fromhex(REAL_SEND_HEX)
        assert transport._sent_frames[0] == expected, (
            f"Expected {expected.hex(' ')}, got {transport._sent_frames[0].hex(' ')}"
        )

    @pytest.mark.asyncio
    async def test_get_brightness_returns_cms_tags_on_real_response(self):
        """验证设备返回真实响应时，get_brightness 返回 CmsTags 且数据正确。"""
        transport = FakeTransport(responses=[bytes.fromhex(REAL_RECV_HEX)])
        device = SanSiCms(transport)

        result = await device.get_brightness()

        # 验证：返回 CmsTags
        assert isinstance(result, CmsTags)
        # 验证：解码数据正确
        # data="115" → mode=1, brightness=15 → round(15/31*100)=48
        assert result.brightness == 48
        # SanSi device.py: mode==0 → "auto", else → "manual"
        # 真实报文 mode=1 → "manual"
        assert result.brightness_mode == "manual"

    @pytest.mark.asyncio
    async def test_get_brightness_uses_correct_what(self):
        """验证 get_brightness 使用 GET_BRIGHTNESS_AND_MODE 指令码。"""
        transport = FakeTransport(responses=[bytes.fromhex(REAL_RECV_HEX)])
        device = SanSiCms(transport)

        await device.get_brightness()

        # 解析发送帧，验证 what=GET_BRIGHTNESS_AND_MODE
        sent_bytes = transport._sent_frames[0]
        # SanSi 请求帧格式：STX(1) + address(2) + what(2) + data + CRC(2) + ETX(1)
        what_bytes = sent_bytes[3:5]
        assert what_bytes == What.GET_BRIGHTNESS_AND_MODE.value

    @pytest.mark.asyncio
    async def test_get_brightness_decodes_real_packet_data_correctly(self):
        """验证 codec 正确解码真实响应数据（mode=1, brightness=48）。

        此测试为 SanSi codec 1字节偏移 bug 的回归测试：
        - 旧版本（bug）：data[1] 取 mode, data[2:4] 取 brightness → mode=1, brightness=16（错误）
        - 修复后：data[0] 取 mode, data[1:3] 取 brightness → mode=1, brightness=48（正确）
        """
        from highway_sdk.vendors.cms.sansi.codec import SanSiCodec

        # 真实数据域 "115"
        result = SanSiCodec.decode_get_brightness(b"115")

        assert result["mode"] == 1
        assert result["brightness"] == 48
