"""诺瓦厂商设备模块。"""

import struct

from highway_sdk.core.device import BaseDevice
from highway_sdk.core.tags import BaseTags

from .codec import NovaCodec
from .spec import ENCODING, Frame, What


class NovaDevice(BaseDevice):
    """诺瓦VMS设备客户端。"""

    codec = NovaCodec

    async def _request(self, frame: Frame, timeout: float = 3.0) -> Frame:
        """发送请求帧并返回解析后的响应帧。"""
        response = await self.request(frame, timeout)
        return Frame.from_bytes(response)

    async def get_brightness(self) -> BaseTags:
        """获取亮度信息。"""
        frame = Frame(what=What.GET_BRIGHTNESS_REQ)
        response = await self._request(frame)
        return self.codec.decode(response)

    async def get_play_item(self) -> BaseTags:
        """获取当前播放项。"""
        frame = Frame(what=What.GET_PLAY_ITEM_REQ)
        response = await self._request(frame)
        return self.codec.decode(response)

    async def get_play_list(self, play_id: int = 0) -> BaseTags:
        """获取播放列表。"""
        frame = Frame(what=What.GET_PLAY_LIST_REQ)
        response = await self._request(frame)
        return self.codec.decode(response)

    async def send_file_name(self, file_name: str = "play001.lst", block_size: int = 65535) -> BaseTags:
        """发送文件名。

        Args:
            file_name: 文件名，默认为 "play001.lst"。
            block_size: 块大小，默认为 65535。
        """
        data = struct.pack("<H", block_size) + file_name.encode(ENCODING)
        frame = Frame(what=What.SEND_FILE_NAME_REQ, data=data)
        response = await self._request(frame)
        return self.codec.decode(response)

    async def send_file_content(self, content: str, block_num: int = 1) -> BaseTags:
        """发送文件内容。

        Args:
            content: 文件内容。
            block_num: 块号，默认为 1。
        """
        data = struct.pack("<H", block_num) + content.encode(ENCODING)
        frame = Frame(what=What.SEND_FILE_CONTENT_REQ, data=data)
        response = await self._request(frame)
        return self.codec.decode(response)

    async def select_play_list(self, playlist_id: int = 1) -> BaseTags:
        """指定播放列表进行播放。

        Args:
            playlist_id: 播放列表 ID，默认为 1。
        """
        data = struct.pack(">B", playlist_id)
        frame = Frame(what=What.SELECT_PLAY_LIST_REQ, data=data)
        response = await self._request(frame)
        return self.codec.decode(response)
