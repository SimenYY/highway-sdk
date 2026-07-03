"""诺瓦厂商编解码器模块。"""

import struct

from highway_sdk.core.codec import BaseCodec
from highway_sdk.core.exceptions import DeviceOperationError
from highway_sdk.core.tags import BaseTags

from ..tags import BrightnessMode, BrightnessTags, ItemTags, PlayTags, ScreenTags
from .spec import ResultCode, What


class NovaCodec(BaseCodec):
    """诺瓦VMS编解码器。"""

    @classmethod
    def _is_ok(cls, data: bytes) -> bool:
        """检查返回是否成功。"""
        return data.startswith(ResultCode.SUCCESS.value)

    @classmethod
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
    @BaseCodec.register(What.GET_PLAY_LIST_RESP)
    def decode_get_play_list(cls, data: bytes) -> PlayTags:
        """解码获取当前播放列表响应。"""
        if not cls._is_ok(data):
            raise DeviceOperationError("Failed to get now play all content")

        # TODO: 需要实现 PlayParser 解析逻辑
        return PlayTags()

    @classmethod
    @BaseCodec.register(What.SEND_FILE_NAME_RESP)
    def decode_send_file_name(cls, data: bytes) -> BaseTags:
        """解码发送文件名响应。"""
        if not cls._is_ok(data):
            raise DeviceOperationError("Failed to send file name")
        return BaseTags()

    @classmethod
    @BaseCodec.register(What.SEND_FILE_CONTENT_RESP)
    def decode_send_file_content(cls, data: bytes) -> BaseTags:
        """解码发送文件内容响应。"""
        if not data[-1:] == b"\x01":
            raise DeviceOperationError("Failed to send file content")
        return BaseTags()

    @classmethod
    @BaseCodec.register(What.FILE_SENT_RESP)
    def decode_file_sent(cls, data: bytes) -> BaseTags:
        """解码文件发送结束响应。"""
        if not cls._is_ok(data):
            raise DeviceOperationError("Failed to send file end")
        return BaseTags()

    @classmethod
    @BaseCodec.register(What.SELECT_PLAY_LIST_RESP)
    def decode_select_play_list(cls, data: bytes) -> BaseTags:
        """解码指定播放列表播放响应。"""
        if not cls._is_ok(data):
            raise DeviceOperationError("Failed to select play list")
        return BaseTags()

    @classmethod
    @BaseCodec.register(What.GET_SCREEN_SIZE_RESP)
    def decode_get_screen_size(cls, data: bytes) -> ScreenTags:
        """解码获取屏幕大小响应。"""
        width, height = struct.unpack("<HH", data)
        return ScreenTags(width=width, height=height)

    @classmethod
    @BaseCodec.register(What.GET_BRIGHTNESS_RESP)
    def decode_get_brightness(cls, data: bytes) -> BrightnessTags:
        """解码获取当前亮度响应。"""
        if len(data) < 2:
            raise DeviceOperationError("Failed to get now brightness")
        mode_val = int(data[0])
        if mode_val not in (BrightnessMode.AUTO, BrightnessMode.MANUAL):
            raise DeviceOperationError(f"Invalid brightness mode: {mode_val}")
        brightness = min(int(data[1]), 100)
        return BrightnessTags(mode=BrightnessMode(mode_val), brightness=brightness)
