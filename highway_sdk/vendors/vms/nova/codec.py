"""诺瓦厂商编解码器模块。"""

from highway_sdk.core.codec import BaseCodec
from highway_sdk.core.tags import BaseTags


class NovaCodec(BaseCodec):
    """诺瓦VMS编解码器。"""

    @classmethod
    def decode_get_brightness(cls, data: bytes) -> BaseTags:
        """解码亮度信息。"""
        return BaseTags()

    @classmethod
    def decode_get_play_item(cls, data: bytes) -> BaseTags:
        """解码播放项信息。"""
        return BaseTags()

    @classmethod
    def decode_get_play_list(cls, data: bytes) -> BaseTags:
        """解码播放列表信息。"""
        return BaseTags()
