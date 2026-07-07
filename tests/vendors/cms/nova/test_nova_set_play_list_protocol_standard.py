"""诺瓦 set_play_list 协议标准报文测试。

报文来源：诺瓦交通协议标准版 V3.11.5（send_file_name + send_file_content + select_play_list 指令）

Nova 的 set_play_list 是三步流程：
1. send_file_name — 发送文件名（携带 block_size）
2. send_file_content — 发送文件内容（携带 block_num）
3. select_play_list — 选择播放列表触发播放

本测试验证：
1. set_play_list 按正确顺序发送三个帧，字节与协议标准报文完全一致
2. 三步均成功时返回 status="success"
3. send_file_name 失败时短路返回 error（不调用后续步骤）
4. send_file_content 失败时短路返回 error（不调用 select_play_list）

注：响应帧无协议标准报文，使用 Frame 类构造成功/失败响应（数据域 0x01=成功，0x00=失败）。
"""

from collections.abc import Sequence

import pytest

from highway_sdk.core.response import Response
from highway_sdk.core.transport import Transport
from highway_sdk.vendors.cms.nova.device import NovaDevice
from highway_sdk.vendors.cms.nova.spec import Frame, What


class FakeTransport(Transport):
    """模拟传输层：记录发送字节并按序返回预设响应。"""

    def __init__(self, responses: Sequence[bytes]):
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


def _build_response(what: What, success: bool = True) -> bytes:
    """使用 Frame 类构造 Nova 响应帧字节。

    Nova 各响应数据域格式（参见 NovaCodec 解码器注释）：
    - 0x12 (SEND_FILE_NAME_RESP): 执行结果 1B（1-成功 / 0-失败）
    - 0x14 (SEND_FILE_CONTENT_RESP): 块号 2B + 执行结果 1B（1-成功 / 0-失败）
    - 0x1C (SELECT_PLAY_LIST_RESP): 执行结果 1B（1-成功 / 0-失败）
    """
    result_byte = b"\x01" if success else b"\x00"
    if what == What.SEND_FILE_CONTENT_RESP:
        # 块号 2B (LE, 默认 1) + 执行结果 1B
        data = b"\x01\x00" + result_byte
    else:
        data = result_byte
    return bytes(Frame(what=what, data=data))


# 协议标准 V3.11.5 上位机发送报文：
# send_file_name: AA FF FF 11 FF FF 70 6C 61 79 30 30 31 2E 6C 73 74 CC 5A 9B
# 数据域: struct.pack("<H", 65535) + "play001.lst".encode("utf-8")
SEND_FILE_NAME_HEX = "aaffff11ffff706c61793030312e6c7374cc5a9b"

# select_play_list: AA FF FF 1B 01 CC BF 28
# 数据域: struct.pack(">B", 1)
SELECT_PLAY_LIST_HEX = "aaffff1b01ccbf28"

# send_file_content 无完整协议标准 hex，仅验证结构：
# AA FF FF 13 01 00 [content] CC [CRC]
# 数据域: struct.pack("<H", block_num=1) + content.encode("utf-8")
TEST_CONTENT = "[all]\r\nitems=1"


class TestNovaSetPlayListProtocolStandard:
    """测试 NovaDevice.set_play_list 与协议标准报文的一致性。"""

    @pytest.mark.asyncio
    async def test_set_play_list_sends_three_frames_in_correct_order(self):
        """验证 set_play_list 按顺序发送 send_file_name、send_file_content、select_play_list。"""
        responses = [
            _build_response(What.SEND_FILE_NAME_RESP, success=True),
            _build_response(What.SEND_FILE_CONTENT_RESP, success=True),
            _build_response(What.SELECT_PLAY_LIST_RESP, success=True),
        ]
        transport = FakeTransport(responses=responses)
        device = NovaDevice(transport)

        await device.set_play_list(TEST_CONTENT, file_name="play001.lst")

        # 验证：发送了三个帧
        assert len(transport._sent_frames) == 3

        # 验证：第一个帧是 send_file_name，与协议标准报文一致
        expected_send_file_name = bytes.fromhex(SEND_FILE_NAME_HEX)
        assert transport._sent_frames[0] == expected_send_file_name, (
            f"Expected send_file_name {expected_send_file_name.hex(' ')}, got {transport._sent_frames[0].hex(' ')}"
        )

        # 验证：第二个帧是 send_file_content（结构验证，因协议标准未提供完整 hex）
        send_file_content_bytes = transport._sent_frames[1]
        assert send_file_content_bytes[0:1] == b"\xaa"  # 起始符
        assert send_file_content_bytes[3:4] == b"\x13"  # SEND_FILE_CONTENT_REQ
        # 数据域前 2 字节为 block_num=1（小端）
        # 注：起始符后可能因转义而偏移，但 0x13 不需转义
        assert send_file_content_bytes[4:6] == b"\x01\x00"

        # 验证：第三个帧是 select_play_list，与协议标准报文一致
        expected_select = bytes.fromhex(SELECT_PLAY_LIST_HEX)
        assert transport._sent_frames[2] == expected_select, (
            f"Expected select_play_list {expected_select.hex(' ')}, got {transport._sent_frames[2].hex(' ')}"
        )

    @pytest.mark.asyncio
    async def test_set_play_list_returns_success_on_all_success(self):
        """验证三步均成功时返回 success。"""
        responses = [
            _build_response(What.SEND_FILE_NAME_RESP, success=True),
            _build_response(What.SEND_FILE_CONTENT_RESP, success=True),
            _build_response(What.SELECT_PLAY_LIST_RESP, success=True),
        ]
        transport = FakeTransport(responses=responses)
        device = NovaDevice(transport)

        result = await device.set_play_list(TEST_CONTENT, file_name="play001.lst")

        assert isinstance(result, Response)
        assert result.status == "success"
        assert result.error_msg is None

    @pytest.mark.asyncio
    async def test_set_play_list_short_circuits_on_send_file_name_failure(self):
        """验证 send_file_name 失败时短路返回 error，不调用后续步骤。"""
        responses = [
            _build_response(What.SEND_FILE_NAME_RESP, success=False),
            # 故意不提供后续响应，若被调用会抛 RuntimeError
        ]
        transport = FakeTransport(responses=responses)
        device = NovaDevice(transport)

        result = await device.set_play_list(TEST_CONTENT, file_name="play001.lst")

        assert result.status == "error"
        # 验证：只发送了 send_file_name 一个帧
        assert len(transport._sent_frames) == 1
        assert transport._sent_frames[0] == bytes.fromhex(SEND_FILE_NAME_HEX)

    @pytest.mark.asyncio
    async def test_set_play_list_short_circuits_on_send_file_content_failure(self):
        """验证 send_file_content 失败时短路返回 error，不调用 select_play_list。"""
        responses = [
            _build_response(What.SEND_FILE_NAME_RESP, success=True),
            _build_response(What.SEND_FILE_CONTENT_RESP, success=False),
            # 故意不提供 select_play_list 响应，若被调用会抛 RuntimeError
        ]
        transport = FakeTransport(responses=responses)
        device = NovaDevice(transport)

        result = await device.set_play_list(TEST_CONTENT, file_name="play001.lst")

        assert result.status == "error"
        # 验证：发送了 send_file_name 和 send_file_content 两个帧（select_play_list 未被调用）
        assert len(transport._sent_frames) == 2

    @pytest.mark.asyncio
    async def test_set_play_list_uses_default_file_name(self):
        """验证 set_play_list 默认使用 'play001.lst' 作为文件名。"""
        responses = [
            _build_response(What.SEND_FILE_NAME_RESP, success=True),
            _build_response(What.SEND_FILE_CONTENT_RESP, success=True),
            _build_response(What.SELECT_PLAY_LIST_RESP, success=True),
        ]
        transport = FakeTransport(responses=responses)
        device = NovaDevice(transport)

        # 不传 file_name，使用默认值
        await device.set_play_list(TEST_CONTENT)

        # 验证：send_file_name 帧使用默认文件名
        assert transport._sent_frames[0] == bytes.fromhex(SEND_FILE_NAME_HEX)
