"""显科厂商设备模块。"""

from highway_sdk.core.device import BaseDevice
from highway_sdk.core.tags import BaseTags

from .codec import XianKeCodec
from .spec import ENCODING, Frame, What


class XianKeDevice(BaseDevice):
    """显科VMS设备客户端。"""

    codec = XianKeCodec

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
        """获取播放列表。"""
        frame = Frame(what=What.GET_PLAY_LIST_NAME)
        response = await self._request(frame)
        return self.codec.decode(response)

    async def upload_file(self, content: str, file_name: str = "list\\000.xkl") -> BaseTags:
        """上传文件。

        Args:
            content: 文件内容。
            file_name: 文件名，默认为 "list\\000.xkl"。
        """
        # 数据域格式: "10" + 文件名长度(3位) + 文件名 + "0000" + 文件内容
        data = b"10"
        data += str(len(file_name)).encode("ascii").rjust(3, b"0")
        data += file_name.encode(ENCODING)
        data += b"0000"  # 文件偏移地址
        data += content.encode(ENCODING)
        frame = Frame(what=What.UPLOAD_FILE, data=data)
        response = await self._request(frame)
        return self.codec.decode(response)

    async def select_play_list(self, file_name: str = "000.xkl") -> BaseTags:
        """选择播放列表进行播放。

        Args:
            file_name: 播放列表文件名，默认为 "000.xkl"。
        """
        data = file_name.encode(ENCODING)
        frame = Frame(what=What.SELECT_PLAY_LIST, data=data)
        response = await self._request(frame)
        return self.codec.decode(response)
