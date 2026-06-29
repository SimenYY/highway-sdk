"""诺瓦厂商设备模块。"""

from highway_sdk.core.device import BaseDevice
from highway_sdk.core.tags import BaseTags
from highway_sdk.core.transport import Transport

from .codec import NovaCodec
from .spec import Frame, What


class NovaDevice(BaseDevice):
    """诺瓦VMS设备客户端。"""

    codec = NovaCodec

    def __init__(self, transport: Transport):
        super().__init__(transport)

    async def get_brightness(self) -> BaseTags:
        """获取亮度信息。"""
        frame = Frame(what=What.GET_BRIGHTNESS_REQ)
        response = await self.request(frame)
        return self.codec.decode_get_brightness(response)

    async def get_play_item(self) -> BaseTags:
        """获取当前播放项。"""
        frame = Frame(what=What.GET_PLAY_ITEM_REQ)
        response = await self.request(frame)
        return self.codec.decode_get_play_item(response)

    async def get_play_list(self, play_id: int = 0) -> BaseTags:
        """获取播放列表。"""
        frame = Frame(what=What.GET_PLAY_LIST_REQ)
        response = await self.request(frame)
        return self.codec.decode_get_play_list(response)
