"""电明厂商设备模块。"""

from highway_sdk.core.device import BaseDevice
from highway_sdk.core.tags import BaseTags

from .codec import DianMingCodec
from .spec import ENCODING, Frame, What


class DianMingDevice(BaseDevice):
    """电明VMS设备客户端。"""

    codec = DianMingCodec

    async def _request(self, frame: Frame, timeout: float = 3.0) -> Frame:
        """发送请求帧并返回解析后的响应帧。"""
        response = await self.request(frame, timeout)
        return Frame.from_bytes(response)

    async def get_brightness(self) -> BaseTags:
        """获取亮度信息。"""
        frame = Frame(what=What.GET_BRIGHTNESS_AND_MODE_REQ)
        response = await self._request(frame)
        return self.codec.decode(response)

    async def get_play_item(self) -> BaseTags:
        """获取当前播放项。"""
        frame = Frame(what=What.GET_PLAY_ITEM_REQ)
        response = await self._request(frame)
        return self.codec.decode(response)

    async def get_play_list(self, play_id: int = 0, filename: str = "play00.lst") -> BaseTags:
        """获取播放列表。

        Args:
            play_id: 播放列表 ID，默认为 0。
            filename: 播放列表文件名，默认为 "play00.lst"。
        """
        # 数据域格式: 8字节偏移量 + 文件名
        offset = f"{play_id:08d}".encode("ascii")
        data = offset + filename.encode("ascii")
        frame = Frame(what=What.GET_PLAY_LIST_REQ, data=data)
        response = await self._request(frame)
        return self.codec.decode(response)

    async def set_brightness(self, brightness: int | None = None) -> BaseTags:
        """设置亮度或控制亮度模式。

        Args:
            brightness: 亮度值(0-31)，None表示自动调节亮度模式。
        """
        if brightness is None:
            data = b"FFFFFF"  # 自动调节亮度
        else:
            brightness = max(0, min(31, brightness))
            # 红、绿、蓝三基色相同，格式为 "RRGGBB"（每段2位十进制 ASCII）
            data = (f"{brightness:02d}" * 3).encode("ascii")
        frame = Frame(what=What.SET_BRIGHTNESS_OR_MODE_REQ, data=data)
        response = await self._request(frame)
        return self.codec.decode(response)

    async def set_play_list(self, content: str, play_id: int = 0) -> BaseTags:
        """下发播放列表并立即显示。

        Args:
            content: 播放列表内容（可由 Play 模型生成）。
            play_id: 播放列表 ID，默认为 0。
        """
        file_name = f"play{play_id:02d}.lst"
        data = b"+00000000" + file_name.encode(ENCODING) + content.encode(ENCODING)
        frame = Frame(what=What.SET_PLAY_LIST_AND_PLAY_REQ, data=data)
        response = await self._request(frame)
        return self.codec.decode(response)
