"""三思 set_play_list 真实报文测试。

报文来源：sdk-v2.x.x protocol.py 实际日志（upload_file 指令） + Play 模型生成内容

SanSi 的 set_play_list 直接委托给 upload_file（上传文件即自动更改当前播放表，
无需额外播放指令），因此本测试验证：
1. set_play_list 将 CmsPlayItem 列表转换为协议内容后构造的发送帧与预期一致
2. 设备返回成功响应时，set_play_list 正常返回（无异常）
3. 设备返回失败响应时，set_play_list 抛 ``DeviceOperationError``
"""

from collections.abc import Sequence

import pytest

from highway_sdk.core.exceptions import DeviceOperationError
from highway_sdk.core.transport import Transport
from highway_sdk.vendors.cms.sansi.device import SanSiDevice
from highway_sdk.vendors.cms.sansi.spec import ENCODING, Bmp, Color, Font, FontSize, Frame, Item, Play, Text, What
from highway_sdk.vendors.cms.tags import CmsPlayItem


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


# 测试输入：基于真实报文 sdk-v2.x.x protocol.py 中播放项的语义构造 CmsPlayItem 列表
# 真实报文中含 2 个图片项（008.bmp, 009.bmp）+ 1 个文本项（高速公路 严禁逆行，宋体 32 黄色）
ITEMS = [
    CmsPlayItem(image_name="008", duration=3),
    CmsPlayItem(image_name="009", duration=3),
    CmsPlayItem(text="高速公路 严禁逆行", font="宋体", font_size=32, font_color="#FFFF00", duration=5),
]

# 预期协议内容（由 SanSiDevice._items_to_content(ITEMS) 生成，等价于 Play 模型序列化）
# 格式：[playlist]\r\nitem_no=N\r\nitem{i}={duration(百分之一秒)},{screen_in},{play_speed},{media}\r\n
EXPECTED_CONTENT = (
    "[playlist]\r\n"
    "item_no=3\r\n"
    "item0=300,1,0,\\C000000\\B008\r\n"
    "item1=300,1,0,\\C000000\\B009\r\n"
    "item2=500,1,0,\\C000000\\fs3232\\c255255000000\\b000000000000"
    "高速公路 严禁逆行"
    "\r\n"
)


def _build_upload_file_frame(file_name: str, content: str) -> bytes:
    """通过 Frame 类构造 SanSi upload_file 发送帧字节（与设备运行时同一路径）。"""
    data = file_name.encode(ENCODING) + b"+" + b"\x00\x00\x00\x00" + content.encode(ENCODING)
    return bytes(Frame(what=What.UPLOAD_FILE, data=data))


def _build_expected_play() -> str:
    """独立构造 Play 模型字符串，用于交叉验证 _items_to_content 的输出。"""
    item_list = [
        Item(
            media_list=[Bmp(x=0, y=0, bmp_file_name="008")],
            duration=300,
            screen_in=1,
            play_speed=0,
        ),
        Item(
            media_list=[Bmp(x=0, y=0, bmp_file_name="009")],
            duration=300,
            screen_in=1,
            play_speed=0,
        ),
        Item(
            media_list=[
                Text(
                    x=0,
                    y=0,
                    font=Font.SONG_TI,
                    font_size=FontSize._32,
                    font_color=Color.YELLOW,
                    background_color=Color.BLACK,
                    text="高速公路 严禁逆行",
                )
            ],
            duration=500,
            screen_in=1,
            play_speed=0,
        ),
    ]
    return str(Play(item_list=item_list))


# sdk-v2.x.x protocol.py 实际日志（成功响应）：
# 接收 02 30 31 30 C5 52 03
# 数据域: "0" (SanSi SUCCESS = b"0")
REAL_RECV_SUCCESS_HEX = "02303130c55203"


def _calc_sansi_crc(payload: bytes) -> bytes:
    """计算 SanSi CRC（与 Frame.calc_crc 一致）。"""
    from highway_sdk.vendors.cms.sansi.spec import Frame

    return Frame.calc_crc(payload)


class TestSanSiSetPlayListRealPacket:
    """测试 SanSiDevice.set_play_list 与预期报文的一致性。"""

    @pytest.mark.asyncio
    async def test_set_play_list_send_frame_matches_expected(self):
        """验证 set_play_list 将 items 转换为协议内容后构造的发送帧与预期一致。"""
        # 准备：模拟传输层，注入成功响应
        transport = FakeTransport(responses=[bytes.fromhex(REAL_RECV_SUCCESS_HEX)])
        device = SanSiDevice(transport)

        # 执行：成功时返回 None
        result = await device.set_play_list(ITEMS, file_name="play.lst")

        # 验证：返回值为 None
        assert result is None
        # 验证：发送字节与预期帧一致
        assert len(transport._sent_frames) == 1
        expected = _build_upload_file_frame("play.lst", EXPECTED_CONTENT)
        assert transport._sent_frames[0] == expected, (
            f"Expected {expected.hex(' ')}, got {transport._sent_frames[0].hex(' ')}"
        )

    def test_items_to_content_matches_play_model(self):
        """验证 _items_to_content 输出与独立构造的 Play 模型字符串一致。"""
        content = SanSiDevice._items_to_content(ITEMS)
        assert content == _build_expected_play()
        assert content == EXPECTED_CONTENT

    @pytest.mark.asyncio
    async def test_set_play_list_returns_none_on_success_response(self):
        """验证设备返回真实成功响应时，set_play_list 正常返回 None。"""
        transport = FakeTransport(responses=[bytes.fromhex(REAL_RECV_SUCCESS_HEX)])
        device = SanSiDevice(transport)

        result = await device.set_play_list(ITEMS, file_name="play.lst")

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
            await device.set_play_list(ITEMS, file_name="play.lst")

    @pytest.mark.asyncio
    async def test_set_play_list_uses_upload_file_what(self):
        """验证 set_play_list 使用 UPLOAD_FILE 指令码（SanSi 上传即播放）。"""
        transport = FakeTransport(responses=[bytes.fromhex(REAL_RECV_SUCCESS_HEX)])
        device = SanSiDevice(transport)

        await device.set_play_list(ITEMS, file_name="play.lst")

        # 解析发送帧，验证 what=UPLOAD_FILE
        sent_bytes = transport._sent_frames[0]
        # SanSi 请求帧格式：STX(1) + address(2) + what(2) + data + CRC(2) + ETX(1)
        what_bytes = sent_bytes[3:5]
        assert what_bytes == What.UPLOAD_FILE.value

    @pytest.mark.asyncio
    async def test_set_play_list_empty_items_raises(self):
        """验证空 items 列表抛 ValueError。"""
        transport = FakeTransport(responses=[bytes.fromhex(REAL_RECV_SUCCESS_HEX)])
        device = SanSiDevice(transport)

        with pytest.raises(ValueError, match="播放列表不能为空"):
            await device.set_play_list([], file_name="play.lst")
