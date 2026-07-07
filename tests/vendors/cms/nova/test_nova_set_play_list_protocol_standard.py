"""诺瓦 set_play_list 协议标准报文测试。

报文来源：诺瓦交通协议标准版 V3.11.5（send_file_name + send_file_content + select_play_list 指令）
        + Nova 设备 INI 协议格式

Nova 的 set_play_list 接收 ``items: list[CmsPlayItem]``，内部将 items 转换为
INI 协议文本后执行三步流程：
1. send_file_name — 发送文件名（携带 block_size）
2. send_file_content — 发送文件内容（携带 block_num）
3. select_play_list — 选择播放列表触发播放

本测试验证：
1. set_play_list 按正确顺序发送三个帧，字节与协议标准报文一致
2. 三步均成功时正常返回（无异常）
3. send_file_name 失败时抛 ``DeviceOperationError``（不调用后续步骤）
4. send_file_content 失败时抛 ``DeviceOperationError``（不调用 select_play_list）
5. _items_to_content 输出与硬编码预期一致

注：响应帧无协议标准报文，使用 Frame 类构造成功/失败响应（数据域 0x01=成功，0x00=失败）。
"""

import struct
from collections.abc import Sequence

import pytest

from highway_sdk.core.exceptions import DeviceOperationError
from highway_sdk.core.transport import Transport
from highway_sdk.vendors.cms.nova.device import NovaDevice
from highway_sdk.vendors.cms.nova.spec import ENCODING, Frame, What
from highway_sdk.vendors.cms.tags import CmsPlayItem


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


# 测试输入：基于 Nova 协议标准 V3.11.5 中播放项的语义构造 CmsPlayItem 列表
# 含 1 个文本项（前方事故 交通堵塞，宋体 32 红色，duration=15 秒）
ITEMS = [
    CmsPlayItem(
        text="前方事故 交通堵塞",
        font="宋体",
        font_size=32,
        font_color="#FF0000",
        duration=15,
    ),
]

# 预期协议内容（由 NovaDevice._items_to_content(ITEMS) 生成）
# 格式：[PLAYLIST]\r\nITEM_NO={count:03d}\r\nITEM{index:03d}={duration},0,0,0,0,{media_str}\r\n
# Nova duration 单位为秒（无需转换），font_size 格式为重复输出（如 32→"3232"）
# 文本媒体串格式：\C000000\F{font_code}{font_size_code}\T{color}\W{text}
EXPECTED_CONTENT = (
    "[PLAYLIST]\r\nITEM_NO=001\r\nITEM000=15,0,0,0,0,\\C000000\\Fs3232\\T255000000000\\W前方事故 交通堵塞\r\n"
)

# 协议标准 V3.11.5 上位机发送报文：
# send_file_name: AA FF FF 11 FF FF 70 6C 61 79 30 30 31 2E 6C 73 74 CC 5A 9B
# 数据域: struct.pack("<H", 65535) + "play001.lst".encode("utf-8")
SEND_FILE_NAME_HEX = "aaffff11ffff706c61793030312e6c7374cc5a9b"

# select_play_list: AA FF FF 1B 01 CC BF 28
# 数据域: struct.pack(">B", 1)
SELECT_PLAY_LIST_HEX = "aaffff1b01ccbf28"


def _build_send_file_content_frame(content: str, block_num: int = 1) -> bytes:
    """通过 Frame 类构造 send_file_content 请求帧字节。

    与 NovaDevice.send_file_content 数据构造逻辑一致：
        data = struct.pack("<H", block_num) + content.encode("utf-8")
    """
    data = struct.pack("<H", block_num) + content.encode(ENCODING)
    return bytes(Frame(what=What.SEND_FILE_CONTENT_REQ, data=data))


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

        await device.set_play_list(ITEMS, file_name="play001.lst")

        # 验证：发送了三个帧
        assert len(transport._sent_frames) == 3

        # 验证：第一个帧是 send_file_name，与协议标准报文一致
        expected_send_file_name = bytes.fromhex(SEND_FILE_NAME_HEX)
        assert transport._sent_frames[0] == expected_send_file_name, (
            f"Expected send_file_name {expected_send_file_name.hex(' ')}, got {transport._sent_frames[0].hex(' ')}"
        )

        # 验证：第二个帧是 send_file_content，与 Frame 构造的预期字节一致
        expected_send_file_content = _build_send_file_content_frame(EXPECTED_CONTENT)
        assert transport._sent_frames[1] == expected_send_file_content, (
            f"Expected send_file_content {expected_send_file_content.hex(' ')}, "
            f"got {transport._sent_frames[1].hex(' ')}"
        )

        # send_file_content 帧的结构验证
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

    def test_items_to_content_matches_expected(self):
        """验证 _items_to_content 输出与硬编码预期一致。"""
        content = NovaDevice._items_to_content(ITEMS)
        assert content == EXPECTED_CONTENT

    @pytest.mark.asyncio
    async def test_set_play_list_returns_none_on_all_success(self):
        """验证三步均成功时正常返回 None。"""
        responses = [
            _build_response(What.SEND_FILE_NAME_RESP, success=True),
            _build_response(What.SEND_FILE_CONTENT_RESP, success=True),
            _build_response(What.SELECT_PLAY_LIST_RESP, success=True),
        ]
        transport = FakeTransport(responses=responses)
        device = NovaDevice(transport)

        result = await device.set_play_list(ITEMS, file_name="play001.lst")

        assert result is None

    @pytest.mark.asyncio
    async def test_set_play_list_raises_on_send_file_name_failure(self):
        """验证 send_file_name 失败时抛 DeviceOperationError，不调用后续步骤。"""
        responses = [
            _build_response(What.SEND_FILE_NAME_RESP, success=False),
            # 故意不提供后续响应，若被调用会抛 RuntimeError
        ]
        transport = FakeTransport(responses=responses)
        device = NovaDevice(transport)

        # 验证：抛 DeviceOperationError
        with pytest.raises(DeviceOperationError):
            await device.set_play_list(ITEMS, file_name="play001.lst")

        # 验证：只发送了 send_file_name 一个帧
        assert len(transport._sent_frames) == 1
        assert transport._sent_frames[0] == bytes.fromhex(SEND_FILE_NAME_HEX)

    @pytest.mark.asyncio
    async def test_set_play_list_raises_on_send_file_content_failure(self):
        """验证 send_file_content 失败时抛 DeviceOperationError，不调用 select_play_list。"""
        responses = [
            _build_response(What.SEND_FILE_NAME_RESP, success=True),
            _build_response(What.SEND_FILE_CONTENT_RESP, success=False),
            # 故意不提供 select_play_list 响应，若被调用会抛 RuntimeError
        ]
        transport = FakeTransport(responses=responses)
        device = NovaDevice(transport)

        # 验证：抛 DeviceOperationError
        with pytest.raises(DeviceOperationError):
            await device.set_play_list(ITEMS, file_name="play001.lst")

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
        await device.set_play_list(ITEMS)

        # 验证：send_file_name 帧使用默认文件名
        assert transport._sent_frames[0] == bytes.fromhex(SEND_FILE_NAME_HEX)

    @pytest.mark.asyncio
    async def test_set_play_list_empty_items_raises(self):
        """验证空 items 列表抛 ValueError。"""
        responses = [
            _build_response(What.SEND_FILE_NAME_RESP, success=True),
            _build_response(What.SEND_FILE_CONTENT_RESP, success=True),
            _build_response(What.SELECT_PLAY_LIST_RESP, success=True),
        ]
        transport = FakeTransport(responses=responses)
        device = NovaDevice(transport)

        with pytest.raises(ValueError, match="播放列表不能为空"):
            await device.set_play_list([], file_name="play001.lst")
