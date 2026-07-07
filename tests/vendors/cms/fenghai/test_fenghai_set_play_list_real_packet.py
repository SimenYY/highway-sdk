"""丰海 set_play_list 真实报文测试。

报文来源：基于 SanSi 报文格式（用户确认 FengHai 与 SanSi upload_file 协议一致）

FengHai 的 set_play_list 直接委托给 upload_file（上传文件即自动更改当前播放表，
无需额外播放指令），与 SanSi 行为一致。但 FengHai 与 SanSi 帧格式有以下差异：
1. FengHai address 默认为 b"\\x00\\x00"（二进制零），SanSi 为 b"00"（ASCII）
2. FengHai 响应帧包含 what 字段，SanSi 响应帧不包含 what 字段
3. FengHai 与 SanSi 的 upload_file 数据域格式相同：file_name + "+" + 4个零字节 + content

本测试验证：
1. set_play_list 构造的发送帧字节与基于 SanSi 真实报文格式推导的预期帧一致
2. 设备返回成功响应时，set_play_list 正常返回（无异常）
3. 设备返回失败响应时，set_play_list 抛 ``DeviceOperationError``
"""

from collections.abc import Sequence

import pytest

from highway_sdk.core.exceptions import DeviceOperationError
from highway_sdk.core.transport import Transport
from highway_sdk.vendors.cms.fenghai.device import FengHaiDevice
from highway_sdk.vendors.cms.fenghai.spec import ENCODING, Frame, What


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


# 真实发送报文内容（与 SanSi 一致，[playlist] INI 格式）
# 内容来源：sdk-v2.x.x protocol.py SanSi upload_file 实际日志
# 注：FengHai Play 模型也使用 [playlist] section（参见 spec.py Play.__str__）
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


def _build_upload_file_frame(file_name: str, content: str) -> bytes:
    """使用 Frame 类构造 FengHai upload_file 发送帧字节。

    与 FengHaiDevice.upload_file 数据构造逻辑一致：
        data = file_name.encode(ENCODING) + b"+" + b"\\x00\\x00\\x00\\x00" + content.encode(ENCODING)
    """
    data = file_name.encode(ENCODING) + b"+" + b"\x00\x00\x00\x00" + content.encode(ENCODING)
    return bytes(Frame(what=What.UPLOAD_FILE, data=data))


def _build_response_frame(success: bool) -> bytes:
    """使用 Frame 类构造 FengHai upload_file 响应帧字节。

    FengHai 响应帧包含 what 字段（与 SanSi 不同）：
        STX + address(2) + what(2) + data + CRC(2) + ETX

    数据域：b"0" (SUCCESS) 或 b"1" (FAILED)
    """
    from highway_sdk.vendors.cms.fenghai.spec import ResultCode

    data = ResultCode.SUCCESS.value if success else ResultCode.FAILED.value
    return bytes(Frame(what=What.UPLOAD_FILE, data=data))


class TestFengHaiSetPlayListRealPacket:
    """测试 FengHaiDevice.set_play_list 与基于 SanSi 报文格式的预期帧一致性。"""

    @pytest.mark.asyncio
    async def test_set_play_list_send_frame_matches_expected(self):
        """验证 set_play_list 发送的帧字节与基于 SanSi 报文格式推导的预期帧一致。

        FengHai 与 SanSi upload_file 数据域格式相同（file_name+"+"+4零字节+content），
        但 FengHai address 为 b"\\x00\\x00"（二进制零），SanSi 为 b"00"（ASCII）。
        """
        # 准备：模拟传输层，注入成功响应
        transport = FakeTransport(responses=[_build_response_frame(success=True)])
        device = FengHaiDevice(transport)

        # 执行：成功时返回 None
        result = await device.set_play_list(REAL_CONTENT, file_name="play.lst")

        # 验证：返回值为 None
        assert result is None
        # 验证：发送字节与预期帧一致
        assert len(transport._sent_frames) == 1
        expected = _build_upload_file_frame("play.lst", REAL_CONTENT)
        assert transport._sent_frames[0] == expected, (
            f"Expected {expected.hex(' ')}, got {transport._sent_frames[0].hex(' ')}"
        )

    @pytest.mark.asyncio
    async def test_set_play_list_returns_none_on_success_response(self):
        """验证设备返回成功响应时，set_play_list 正常返回 None。"""
        transport = FakeTransport(responses=[_build_response_frame(success=True)])
        device = FengHaiDevice(transport)

        result = await device.set_play_list(REAL_CONTENT, file_name="play.lst")

        assert result is None

    @pytest.mark.asyncio
    async def test_set_play_list_raises_on_failure_response(self):
        """验证设备返回失败响应时，set_play_list 抛 DeviceOperationError。

        失败响应数据域 = b"1" (ResultCode.FAILED)。
        """
        transport = FakeTransport(responses=[_build_response_frame(success=False)])
        device = FengHaiDevice(transport)

        with pytest.raises(DeviceOperationError):
            await device.set_play_list(REAL_CONTENT, file_name="play.lst")

    @pytest.mark.asyncio
    async def test_set_play_list_uses_upload_file_what(self):
        """验证 set_play_list 使用 UPLOAD_FILE 指令码（FengHai 上传即播放）。"""
        transport = FakeTransport(responses=[_build_response_frame(success=True)])
        device = FengHaiDevice(transport)

        await device.set_play_list(REAL_CONTENT, file_name="play.lst")

        # 解析发送帧，验证 what=UPLOAD_FILE
        sent_bytes = transport._sent_frames[0]
        # FengHai 请求帧格式：STX(1) + address(2) + what(2) + data + CRC(2) + ETX(1)
        # address 默认为 b"\x00\x00"（二进制零），what 在 bytes[3:5]
        what_bytes = sent_bytes[3:5]
        assert what_bytes == What.UPLOAD_FILE.value

    @pytest.mark.asyncio
    async def test_set_play_list_response_includes_what_field(self):
        """验证 FengHai 响应帧包含 what 字段（与 SanSi 不同）。

        FengHai 响应格式：STX + address(2) + what(2) + data + CRC(2) + ETX
        SanSi 响应格式：STX + address(2) + data + CRC(2) + ETX（无 what）
        """
        # 验证 _build_response_frame 生成的响应可以被 Frame.from_bytes 正确解析
        response_bytes = _build_response_frame(success=True)
        frame = Frame.from_bytes(response_bytes)

        # FengHai 响应帧 what 应为 UPLOAD_FILE
        assert frame.what == What.UPLOAD_FILE
        # 数据域应为 SUCCESS
        from highway_sdk.vendors.cms.fenghai.spec import ResultCode

        assert frame.data == ResultCode.SUCCESS.value
