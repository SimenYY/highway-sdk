"""显科厂商设备模块。"""

from highway_sdk.core.device import BaseDevice
from highway_sdk.core.tags import BaseTags

from .codec import XianKeCodec
from .spec import Frame, What


class XianKeDevice(BaseDevice):
    """显科VMS设备客户端。"""

    codec = XianKeCodec

    async def get_brightness(self) -> BaseTags:
        """获取亮度信息。"""
        frame = Frame(what=What.GET_BRIGHTNESS_AND_MODE)
        response = await self.request(frame)
        return self.codec.decode(Frame(what=What.GET_BRIGHTNESS_AND_MODE, data=response))

    async def get_play_item(self) -> BaseTags:
        """获取当前播放项。"""
        frame = Frame(what=What.GET_PLAY_ITEM)
        response = await self.request(frame)
        return self.codec.decode(Frame(what=What.GET_PLAY_ITEM, data=response))

    async def get_play_list(self, play_id: int = 0) -> BaseTags:
        """获取播放列表。"""
        frame = Frame(what=What.GET_PLAY_LIST_NAME)
        response = await self.request(frame)
        return self.codec.decode(Frame(what=What.GET_PLAY_LIST_NAME, data=response))
