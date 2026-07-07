"""三思 set_play_list 真实报文测试。

报文来源：sdk-v2.x.x protocol.py 实际日志（upload_file 指令）

SanSi 的 set_play_list 直接委托给 upload_file（上传文件即自动更改当前播放表，
无需额外播放指令），因此本测试验证：
1. set_play_list 构造的发送帧与真实设备日志字节完全一致
2. 设备返回成功响应时，set_play_list 正常返回（无异常）
3. 设备返回失败响应时，set_play_list 抛 ``DeviceOperationError``
"""

from collections.abc import Sequence

import pytest

from highway_sdk.core.exceptions import DeviceOperationError
from highway_sdk.core.transport import Transport
from highway_sdk.vendors.cms.sansi.device import SanSiDevice
from highway_sdk.vendors.cms.sansi.spec import What


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


# 真实发送报文（sdk-v2.x.x protocol.py upload_file 实际日志）
# 内容：[playlist]\r\nnwindows=2\r\nwindows0_x=0\r\nwindows0_y=0\r\nwindows0_w=512\r\n
#       windows0_h=300\r\nitem_no=2\r\nitem0=300,1,0,\B008\r\nitem1=300,1,0,\B009\r\n
#       windows1_x=0\r\nwindows1_y=300\r\nwindows1_w=512\r\nwindows1_h=84\r\n
#       windows1_item_no=1\r\nwindows1_item0=500,1,0,\fs3232\c255255000000高速公路 严禁逆行\r\n
REAL_CONTENT = (
    "[playlist]\r\n"
    "nwindows=2\r\n"
    "windows0_x=0\r\n"
    "windows0_y=0\r\n"
    "windows0_w=512\r\n"
    "windows0_h=300\r\n"
    "item_no=2\r\n"
    "item0=300,1,0,\\B008\r\n"
    "item1=300,1,0,\\B009\r\n"
    "windows1_x=0\r\n"
    "windows1_y=300\r\n"
    "windows1_w=512\r\n"
    "windows1_h=84\r\n"
    "windows1_item_no=1\r\n"
    "windows1_item0=500,1,0,\\fs3232\\c255255000000"
    "高速公路 严禁逆行"
    "\r\n"
)

# sdk-v2.x.x protocol.py 实际日志：
# 发送 02 30 30 31 30 70 6C 61 79 2E 6C 73 74 2B 00 00 00 00 5B 70 6C 61 79 6C 69
#      73 74 5D 0D 0A 6E 77 69 6E 64 6F 77 73 3D 32 0D 0A 77 69 6E 64 6F 77 73 30
#      5F 78 3D 30 0D 0A 77 69 6E 64 6F 77 73 30 5F 79 3D 30 0D 0A 77 69 6E 64 6F
#      77 73 30 5F 77 3D 35 31 32 0D 0A 77 69 6E 64 6F 77 73 30 5F 68 3D 33 30 30
#      0D 0A 69 74 65 6D 5F 6E 6F 3D 32 0D 0A 69 74 65 6D 30 3D 33 30 30 2C 31 2C
#      30 2C 5C 42 30 30 38 0D 0A 69 74 65 6D 31 3D 33 30 30 2C 31 2C 30 2C 5C 42
#      30 30 39 0D 0A 77 69 6E 64 6F 77 73 31 5F 78 3D 30 0D 0A 77 69 6E 64 6F 77
#      73 31 5F 79 3D 33 30 30 0D 0A 77 69 6E 64 6F 77 73 31 5F 77 3D 35 31 32 0D
#      0A 77 69 6E 64 6F 77 73 31 5F 68 3D 38 34 0D 0A 77 69 6E 64 6F 77 73 31 5F
#      69 74 65 6D 5F 6E 6F 3D 31 0D 0A 77 69 6E 64 6F 77 73 31 5F 69 74 65 6D 30
#      3D 35 30 30 2C 31 2C 30 2C 5C 66 73 33 32 33 32 5C 63 32 35 35 32 35 35 30
#      30 30 30 30 30 B8 DF CB D9 B9 AB C2 B7 20 D1 CF BD FB C4 E6 D0 D0 0D 0A EF
#      BD 03
# 注：完整 hex 通过 Frame 类构造（与设备运行时同一路径），避免人工转录 hex 错误。
REAL_SEND_HEX_FULL = (
    "0230303130706c61792e6c73742b00000000"
    "5b706c61796c6973745d0d0a"
    "6e77696e646f77733d320d0a"
    "77696e646f7773305f783d300d0a"
    "77696e646f7773305f793d300d0a"
    "77696e646f7773305f773d3531320d0a"
    "77696e646f7773305f683d3330300d0a"
    "6974656d5f6e6f3d320d0a"
    "6974656d303d3330302c312c302c5c423030380d0a"
    "6974656d313d3330302c312c302c5c423030390d0a"
    "77696e646f7773315f783d300d0a"
    "77696e646f7773315f793d3330300d0a"
    "77696e646f7773315f773d3531320d0a"
    "77696e646f7773315f683d38340d0a"
    "77696e646f7773315f6974656d5f6e6f3d310d0a"
    "77696e646f7773315f6974656d303d3530302c312c302c5c667333323332"
    "5c63323535323535303030303030"
    "b8dfcbd9b9abc2b720d1cfbdfbc4e6d0d00d0a"
    "efbd03"
)

# sdk-v2.x.x protocol.py 实际日志（成功响应）：
# 接收 02 30 31 30 C5 52 03
# 数据域: "0" (SanSi SUCCESS = b"0")
REAL_RECV_SUCCESS_HEX = "02303130c55203"

# 失败响应构造：数据域 "1" (SanSi FAILED = b"1")
# 注：v2.x.x protocol.py 未提供失败响应实际日志，此处基于 SanSi ResultCode 定义构造
REAL_RECV_FAILURE_HEX = "02303131" + "0000"  # 占位，下面运行时计算


def _calc_sansi_crc(payload: bytes) -> bytes:
    """计算 SanSi CRC（与 Frame.calc_crc 一致）。"""
    from highway_sdk.vendors.cms.sansi.spec import Frame

    return Frame.calc_crc(payload)


class TestSanSiSetPlayListRealPacket:
    """测试 SanSiDevice.set_play_list 与真实报文的一致性。"""

    @pytest.mark.asyncio
    async def test_set_play_list_send_frame_matches_real_packet(self):
        """验证 set_play_list 发送的帧字节与真实设备日志完全一致。"""
        # 准备：模拟传输层，注入成功响应
        transport = FakeTransport(responses=[bytes.fromhex(REAL_RECV_SUCCESS_HEX)])
        device = SanSiDevice(transport)

        # 执行：成功时返回 None
        result = await device.set_play_list(REAL_CONTENT, file_name="play.lst")

        # 验证：返回值为 None
        assert result is None
        # 验证：发送字节与真实报文完全一致
        assert len(transport._sent_frames) == 1
        expected = bytes.fromhex(REAL_SEND_HEX_FULL)
        assert transport._sent_frames[0] == expected, (
            f"Expected {expected.hex(' ')}, got {transport._sent_frames[0].hex(' ')}"
        )

    @pytest.mark.asyncio
    async def test_set_play_list_returns_none_on_success_response(self):
        """验证设备返回真实成功响应时，set_play_list 正常返回 None。"""
        transport = FakeTransport(responses=[bytes.fromhex(REAL_RECV_SUCCESS_HEX)])
        device = SanSiDevice(transport)

        result = await device.set_play_list(REAL_CONTENT, file_name="play.lst")

        assert result is None

    @pytest.mark.asyncio
    async def test_set_play_list_raises_on_failure_response(self):
        """验证设备返回失败响应时，set_play_list 抛 DeviceOperationError。

        失败响应数据域 = b"1" (ResultCode.FAILED)。
        """
        # 构造失败响应帧：address="01" + data="1" + CRC
        # SanSi 响应帧无 what，CRC 校验范围 = address + data = b"01" + b"1"
        crc = _calc_sansi_crc(b"01" + b"1")
        failure_frame = b"\x02" + b"01" + b"1" + crc + b"\x03"

        transport = FakeTransport(responses=[failure_frame])
        device = SanSiDevice(transport)

        with pytest.raises(DeviceOperationError):
            await device.set_play_list(REAL_CONTENT, file_name="play.lst")

    @pytest.mark.asyncio
    async def test_set_play_list_uses_upload_file_what(self):
        """验证 set_play_list 使用 UPLOAD_FILE 指令码（SanSi 上传即播放）。"""
        transport = FakeTransport(responses=[bytes.fromhex(REAL_RECV_SUCCESS_HEX)])
        device = SanSiDevice(transport)

        await device.set_play_list(REAL_CONTENT, file_name="play.lst")

        # 解析发送帧，验证 what=UPLOAD_FILE
        sent_bytes = transport._sent_frames[0]
        # SanSi 请求帧格式：STX(1) + address(2) + what(2) + data + CRC(2) + ETX(1)
        what_bytes = sent_bytes[3:5]
        assert what_bytes == What.UPLOAD_FILE.value
