"""诺瓦厂商编解码器模块。"""

import struct
from functools import lru_cache

from highway_sdk.core.codec import BaseCodec
from highway_sdk.core.exceptions import DeviceOperationError
from highway_sdk.core.tags import BaseTags

from ..tags import BrightnessTags, ItemTags, PlayTags
from .spec import ResultCode, What


class NovaCodec(BaseCodec):
    """诺瓦VMS编解码器。"""

    @classmethod
    def _is_ok(cls, data: bytes) -> bool:
        """检查返回是否成功。"""
        return data.startswith(ResultCode.SUCCESS.value)

    @classmethod
    @lru_cache
    @BaseCodec.register(What.GET_PLAY_ITEM_RESP)
    def decode_get_play_item(cls, data: bytes) -> ItemTags:
        """解码获取当前播放内容响应。"""
        tags = ItemTags()
        if cls._is_ok(data):
            content = data[1:].decode("utf-8", errors="ignore")
            tags.text = content
        else:
            raise DeviceOperationError("Failed to get now play content")
        return tags

    @classmethod
    @lru_cache
    @BaseCodec.register(What.GET_PLAY_LIST_RESP)
    def decode_get_play_list(cls, data: bytes) -> PlayTags:
        """解码获取当前播放列表响应。"""
        if not cls._is_ok(data):
            raise DeviceOperationError("Failed to get now play all content")

        # TODO: 需要实现 PlayParser 解析逻辑
        return PlayTags()

    @classmethod
    @lru_cache
    @BaseCodec.register(What.SEND_FILE_NAME_RESP)
    def decode_send_file_name(cls, data: bytes) -> BaseTags:
        """解码发送文件名响应。"""
        if not cls._is_ok(data):
            raise DeviceOperationError("Failed to send file name")
        return BaseTags()

    @classmethod
    @lru_cache
    @BaseCodec.register(What.SEND_FILE_CONTENT_RESP)
    def decode_send_file_content(cls, data: bytes) -> BaseTags:
        """解码发送文件内容响应。"""
        if not data[-1:] == b"\x01":
            raise DeviceOperationError("Failed to send file content")
        return BaseTags()

    @classmethod
    @lru_cache
    @BaseCodec.register(What.FILE_SENT_RESP)
    def decode_file_sent(cls, data: bytes) -> BaseTags:
        """解码文件发送结束响应。"""
        if not cls._is_ok(data):
            raise DeviceOperationError("Failed to send file end")
        return BaseTags()

    @classmethod
    @lru_cache
    @BaseCodec.register(What.SELECT_PLAY_LIST_RESP)
    def decode_select_play_list(cls, data: bytes) -> BaseTags:
        """解码指定播放列表播放响应。"""
        if not cls._is_ok(data):
            raise DeviceOperationError("Failed to select play list")
        return BaseTags()

    @classmethod
    @lru_cache
    @BaseCodec.register(What.GET_SCREEN_SIZE_RESP)
    def decode_get_screen_size(cls, data: bytes) -> BaseTags:
        """解码获取屏幕大小响应。"""
        width, height = struct.unpack("<HH", data)
        return BaseTags(width=width, height=height)

    @classmethod
    @lru_cache
    @BaseCodec.register(What.GET_BRIGHTNESS_RESP)
    def decode_get_brightness(cls, data: bytes) -> BrightnessTags:
        """解码获取当前亮度响应。"""
        tags = BrightnessTags()
        if len(data) >= 2:
            tags.mode = int(data[0])
            tags.brightness = int(data[1])
        else:
            raise DeviceOperationError("Failed to get now brightness")
        return tags
