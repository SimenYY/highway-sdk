"""丰海厂商设备模块。"""

from highway_sdk.core.device import BaseDevice
from highway_sdk.core.tags import BaseTags

from .codec import FengHaiCodec
from .spec import ENCODING, Frame, What


class FengHaiDevice(BaseDevice):
    """丰海VMS设备客户端。"""

    codec = FengHaiCodec

    async def _request(self, frame: Frame, timeout: float = 3.0) -> Frame:
        """发送请求帧并返回解析后的响应帧。"""
        response = await self.request(frame, timeout)
        return Frame.from_bytes(response)

    async def get_brightness(self) -> BaseTags:
        """获取亮度信息。"""
        frame = Frame(what=What.GET_BRIGHTNESS_AND_MODE)
        response = await self._request(frame)
        return self.codec.decode(response)

    async def get_play_item(self) -> BaseTags:
        """获取当前播放项。"""
        frame = Frame(what=What.GET_PLAY_ITEM)
        response = await self._request(frame)
        return self.codec.decode(response)

    async def get_play_list(self, play_id: int = 0) -> BaseTags:
        """获取播放列表（通过下载文件命令）。"""
        frame = Frame(what=What.DOWNLOAD_FILE)
        response = await self._request(frame)
        return self.codec.decode(response)

    async def set_brightness(self, brightness: int) -> BaseTags:
        """设置亮度。

        Args:
            brightness: 亮度值，范围0-31。
        """
        brightness = max(0, min(31, brightness))
        # 红、绿、蓝三基色相同，每段2位十进制 ASCII
        data = (f"{brightness:02d}".encode("ascii")) * 3
        frame = Frame(what=What.SET_BRIGHTNESS, data=data)
        response = await self._request(frame)
        return self.codec.decode(response)

    async def upload_file(self, content: str, file_name: str = "play.lst") -> BaseTags:
        """上传播放列表文件。

        Args:
            content: 文件内容。
            file_name: 文件名，默认为 "play.lst"。
        """
        data = file_name.encode(ENCODING) + b"+" + b"\x00\x00\x00\x00" + content.encode(ENCODING)
        frame = Frame(what=What.UPLOAD_FILE, data=data)
        response = await self._request(frame)
        return self.codec.decode(response)
