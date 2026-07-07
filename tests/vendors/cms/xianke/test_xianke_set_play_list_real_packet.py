"""显科 set_play_list 真实报文测试。

报文来源：sdk-v2.x.x protocol.py 实际日志（upload_file + select_play_list 指令）
        + Play 模型生成内容

XianKe 的 set_play_list 接收 ``items: list[CmsPlayItem]``，内部转换为协议内容后
执行两步流程：
1. upload_file — 上传文件到设备
2. select_play_list — 选择播放列表触发播放

本测试验证：
1. set_play_list 按正确顺序发送两个帧，字节与基于真实设备日志格式的预期一致
2. 两步均成功时正常返回（无异常）
3. upload_file 失败时抛 ``DeviceOperationError``（不调用 select_play_list）
4. _items_to_content 输出与独立构造的 Play 模型字符串一致

注：expected 帧字节通过 Frame 类构造（与设备运行时同一路径），避免人工转录 hex 错误。
真实报文 ground truth 来自 sdk-v2.x.x protocol.py 注释中的实际日志。
"""

from collections.abc import Sequence

import pytest

from highway_sdk.core.exceptions import DeviceOperationError
from highway_sdk.core.transport import Transport
from highway_sdk.vendors.cms.tags import CmsPlayItem
from highway_sdk.vendors.cms.xianke.device import XianKeDevice
from highway_sdk.vendors.cms.xianke.spec import (
    ENCODING,
    Color,
    Font,
    FontSize,
    Frame,
    Item,
    Play,
    ScreenInOut,
    Text,
    What,
)


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


# 测试输入：基于 sdk-v2.x.x protocol.py 实际日志中播放项的语义构造 CmsPlayItem 列表
# 真实报文中含 2 个文本项（深圳显科科技有限公司，宋体 32，红色/绿色）
ITEMS = [
    CmsPlayItem(text="深圳显科科技有限公司", font="宋体", font_size=32, font_color="#FF0000", duration=2),
    CmsPlayItem(text="深圳显科科技有限公司", font="宋体", font_size=32, font_color="#00FF00", duration=2),
]

# 预期协议内容（由 XianKeDevice._items_to_content(ITEMS) 生成，等价于 Play 模型序列化）
# 格式：[LIST]\r\nItemCount=N(3位)\r\nItem{ii}={duration},{screen_in},{play_effect},{screen_out},{play_speed},{media}\r\n
# XianKe Item.duration 单位为秒（无需转换），font_size 格式为 2 位数字（如 32→"32"）
EXPECTED_CONTENT = (
    "[LIST]\r\n"
    "ItemCount=002\r\n"
    "Item00=2,1,0,1,1,\\C000000\\Fs32\\T255000000000\\B000000000000\\U深圳显科科技有限公司\r\n"
    "Item01=2,1,0,1,1,\\C000000\\Fs32\\T000255000000\\B000000000000\\U深圳显科科技有限公司\r\n"
)

# 真实文件名（sdk-v2.x.x protocol.py 实际日志）
# upload_file 的 file_name = "list\000.xkl"（12 字节，含路径前缀）
# select_play_list 的 file_name = "000.xkl"（7 字节，basename）
UPLOAD_FILE_NAME = "list\\000.xkl"
SELECT_FILE_NAME = "000.xkl"


def _build_upload_file_frame(file_name: str, content: str) -> bytes:
    """通过 Frame 类构造 upload_file 请求帧字节（与设备运行时同一路径）。"""
    data = b"10"
    data += str(len(file_name)).encode("ascii").rjust(3, b"0")
    data += file_name.encode(ENCODING)
    data += b"0000"
    data += content.encode(ENCODING)
    return bytes(Frame(what=What.UPLOAD_FILE, data=data))


def _build_select_play_list_frame(file_name: str) -> bytes:
    """通过 Frame 类构造 select_play_list 请求帧字节。"""
    data = file_name.encode(ENCODING)
    return bytes(Frame(what=What.SELECT_PLAY_LIST, data=data))


def _build_expected_play() -> str:
    """独立构造 Play 模型字符串，用于交叉验证 _items_to_content 的输出。"""
    item_list = [
        Item(
            media_list=[
                Text(
                    x=0,
                    y=0,
                    font=Font.SONG_TI,
                    font_size=FontSize._32,
                    font_color=Color.RED,
                    background_color=Color.BLACK,
                    text="深圳显科科技有限公司",
                )
            ],
            duration=2,
            screen_in=ScreenInOut.NORMAL,
            play_effect=0,
            screen_out=ScreenInOut.NORMAL,
            play_speed=1,
        ),
        Item(
            media_list=[
                Text(
                    x=0,
                    y=0,
                    font=Font.SONG_TI,
                    font_size=FontSize._32,
                    font_color=Color.GREEN,
                    background_color=Color.BLACK,
                    text="深圳显科科技有限公司",
                )
            ],
            duration=2,
            screen_in=ScreenInOut.NORMAL,
            play_effect=0,
            screen_out=ScreenInOut.NORMAL,
            play_speed=1,
        ),
    ]
    return str(Play(item_list=item_list))


# sdk-v2.x.x protocol.py 实际日志（upload_file 成功响应）：
# 接收 02 32 30 30 30 01 B4 95 03
# 数据域: 0x01 (XianKe SUCCESS)
UPLOAD_RECV_SUCCESS_HEX = "0232303030 01b49503".replace(" ", "")

# sdk-v2.x.x protocol.py 实际日志（select_play_list 成功响应）：
# 接收 02 32 32 30 30 01 59 FD 03
# 数据域: 0x01 (XianKe SUCCESS)
SELECT_RECV_SUCCESS_HEX = "0232323030 0159fd03".replace(" ", "")


def _calc_xianke_crc(payload: bytes) -> bytes:
    """计算 XianKe CRC（与 Frame.calc_crc 一致）。"""
    return Frame.calc_crc(payload)


class TestXianKeSetPlayListRealPacket:
    """测试 XianKeDevice.set_play_list 与真实报文的一致性。"""

    @pytest.mark.asyncio
    async def test_set_play_list_sends_two_frames_in_correct_order(self):
        """验证 set_play_list 按顺序发送 upload_file 和 select_play_list 两个帧。

        真实报文 ground truth：
        - upload_file 发送: 02 32 30 30 30 31 30 30 31 32 6C 69 73 74 5C 30 30 30 2E 78 6B 6C
                           30 30 30 30 [content] 4D EF 03
        - select_play_list 发送: 02 32 32 30 30 30 30 30 2E 78 6B 6C 7A 93 03
        """
        transport = FakeTransport(
            responses=[
                bytes.fromhex(UPLOAD_RECV_SUCCESS_HEX),
                bytes.fromhex(SELECT_RECV_SUCCESS_HEX),
            ]
        )
        device = XianKeDevice(transport)

        await device.set_play_list(ITEMS, file_name=UPLOAD_FILE_NAME)

        # 验证：发送了两个帧
        assert len(transport._sent_frames) == 2

        # 验证：第一个帧是 upload_file，与 Frame 构造的预期字节一致
        expected_upload = _build_upload_file_frame(UPLOAD_FILE_NAME, EXPECTED_CONTENT)
        assert transport._sent_frames[0] == expected_upload, (
            f"Expected upload_file {expected_upload.hex(' ')}, got {transport._sent_frames[0].hex(' ')}"
        )

        # 验证：upload_file 帧与真实报文前缀一致
        # sdk-v2.x.x protocol.py 实际日志前缀：
        # 02 32 30 30 30 31 30 30 31 32 6C 69 73 74 5C 30 30 30 2E 78 6B 6C 30 30 30 30
        expected_prefix = bytes.fromhex(
            "02323030303130303132"  # STX + what("20") + address("00") + "10" + "012"
            "6c6973745c3030302e786b6c"  # "list\000.xkl"
            "30303030"  # "0000"
        )
        assert transport._sent_frames[0].startswith(expected_prefix), (
            f"Expected prefix {expected_prefix.hex(' ')}, "
            f"got {transport._sent_frames[0][: len(expected_prefix)].hex(' ')}"
        )

        # 验证：upload_file 帧中包含 [LIST] 头和 ItemCount
        assert b"[LIST]\r\nItemCount=002\r\n" in transport._sent_frames[0]

        # 验证：第二个帧是 select_play_list，与 Frame 构造的预期字节一致
        expected_select = _build_select_play_list_frame(SELECT_FILE_NAME)
        assert transport._sent_frames[1] == expected_select, (
            f"Expected select_play_list {expected_select.hex(' ')}, got {transport._sent_frames[1].hex(' ')}"
        )

    def test_items_to_content_matches_play_model(self):
        """验证 _items_to_content 输出与独立构造的 Play 模型字符串一致。"""
        content = XianKeDevice._items_to_content(ITEMS)
        assert content == _build_expected_play()
        assert content == EXPECTED_CONTENT

    @pytest.mark.asyncio
    async def test_set_play_list_returns_none_on_both_success(self):
        """验证两步均成功时正常返回 None。"""
        transport = FakeTransport(
            responses=[
                bytes.fromhex(UPLOAD_RECV_SUCCESS_HEX),
                bytes.fromhex(SELECT_RECV_SUCCESS_HEX),
            ]
        )
        device = XianKeDevice(transport)

        result = await device.set_play_list(ITEMS, file_name=UPLOAD_FILE_NAME)

        assert result is None

    @pytest.mark.asyncio
    async def test_set_play_list_raises_on_upload_failure(self):
        """验证 upload_file 失败时抛 DeviceOperationError，不调用 select_play_list。

        失败响应构造：数据域 = 0x00 (XianKe FAILED)。
        实际日志中无失败响应报文，此处基于 XianKe ResultCode 定义构造。
        """
        # 构造 upload_file 失败响应：what="20" + address="00" + data=0x00 + CRC + ETX
        payload = b"20" + b"00" + b"\x00"  # what + address + data
        crc = _calc_xianke_crc(payload)
        upload_failure = b"\x02" + payload + crc + b"\x03"

        transport = FakeTransport(responses=[upload_failure])
        device = XianKeDevice(transport)

        # 验证：抛 DeviceOperationError
        with pytest.raises(DeviceOperationError):
            await device.set_play_list(ITEMS, file_name=UPLOAD_FILE_NAME)

        # 验证：只发送了 upload_file 一个帧（select_play_list 未被调用）
        assert len(transport._sent_frames) == 1

    @pytest.mark.asyncio
    async def test_set_play_list_extracts_basename_for_select(self):
        """验证 select_play_list 使用 file_name 的 basename（去掉路径前缀）。

        真实报文中：
        - upload_file 的 file_name = "list\\000.xkl"（含路径前缀）
        - select_play_list 的 file_name = "000.xkl"（仅 basename）
        """
        transport = FakeTransport(
            responses=[
                bytes.fromhex(UPLOAD_RECV_SUCCESS_HEX),
                bytes.fromhex(SELECT_RECV_SUCCESS_HEX),
            ]
        )
        device = XianKeDevice(transport)

        await device.set_play_list(ITEMS, file_name=UPLOAD_FILE_NAME)

        # 验证：select_play_list 帧的数据域是 basename "000.xkl"
        select_frame_bytes = transport._sent_frames[1]
        select_frame = Frame.from_bytes(select_frame_bytes)
        assert select_frame.what == What.SELECT_PLAY_LIST
        assert select_frame.data == SELECT_FILE_NAME.encode(ENCODING)

    @pytest.mark.asyncio
    async def test_set_play_list_empty_items_raises(self):
        """验证空 items 列表抛 ValueError。"""
        transport = FakeTransport(
            responses=[
                bytes.fromhex(UPLOAD_RECV_SUCCESS_HEX),
                bytes.fromhex(SELECT_RECV_SUCCESS_HEX),
            ]
        )
        device = XianKeDevice(transport)

        with pytest.raises(ValueError, match="播放列表不能为空"):
            await device.set_play_list([], file_name=UPLOAD_FILE_NAME)
