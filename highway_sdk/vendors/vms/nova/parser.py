from functools import lru_cache
from highway_sdk.core.exceptions import (
    DeviceOperationError,
)
from highway_sdk.vendors.vms._tags import ItemTags, BrightnessTags
from highway_sdk.vendors.vms._base import BaseParser
from .spec import What, ResultCode
from .media import PlayParser


class Parser(BaseParser):
    @classmethod
    def _is_ok(cls, data: bytes):
        """检查返回是否成功"""
        return data.startswith(ResultCode.SUCCESS.value)


@lru_cache
@Parser.register(What.GET_PLAY_ITEM_RESP)
def _parse_get_play_item(data: bytes):
    """解析获取当前播放内容响应"""
    tags = ItemTags()
    if Parser._is_ok(data):
        # 解析当前播放内容，根据实际返回格式调整
        content = data[1:].decode("utf-8", errors="ignore")
        tags.text = content
    else:
        raise DeviceOperationError("Failed to get now play content")
    return tags


@lru_cache
@Parser.register(What.GET_PLAY_LIST_RESP)
def _parse_get_play_list(data: bytes):
    """解析获取当前播放列表响应"""
    if not Parser._is_ok(data):
        raise DeviceOperationError("Failed to get now play all content")

    # 解析播放列表内容
    content = data[1:].decode("utf-8", errors="ignore")
    return PlayParser.parse(content).build()


@lru_cache
@Parser.register(What.SEND_FILE_NAME_RESP)
def _parse_send_file_name(data: bytes):
    """解析发送文件名响应"""
    if not Parser._is_ok(data):
        raise DeviceOperationError("Failed to send file name")
    return {"status": "success"}


@lru_cache
@Parser.register(What.SEND_FILE_CONTENT_RESP)
def _parse_send_file_content(data: bytes):
    """解析发送文件内容响应"""
    if not data[-1:] == b"\x01":
        raise DeviceOperationError("Failed to send file content")
    return {"status": "success"}


@lru_cache
@Parser.register(What.FILE_SENT_RESP)
def _parse_file_sent(data: bytes):
    """解析文件发送结束响应"""
    if not Parser._is_ok(data):
        raise DeviceOperationError("Failed to send file end")
    return {"status": "success"}


@lru_cache
@Parser.register(What.SELECT_PLAY_LIST_RESP)
def _parse_select_play_list(data: bytes):
    """解析指定播放列表播放响应"""
    if not Parser._is_ok(data):
        raise DeviceOperationError("Failed to select play list")
    return {"status": "success"}


@lru_cache
@Parser.register(What.GET_SCREEN_SIZE_RESP)
def _parse_get_screen_size(data: bytes):
    """解析获取屏幕大小响应"""
    # 解析屏幕大小，格式：宽度2字节(小端) + 高度2字节(小端)
    import struct

    width, height = struct.unpack("<HH", data)
    return {"width": width, "height": height}


@lru_cache
@Parser.register(What.GET_BRIGHTNESS_RESP)
def _parse_get_brightness(data: bytes):
    """解析获取当前亮度响应"""
    tags = BrightnessTags()
    if len(data) >= 2:
        # 格式：控制模式1字节 + 亮度值1字节
        tags.mode = int(data[0])
        tags.brightness = int(data[1])
    else:
        raise DeviceOperationError("Failed to get now brightness")
    return tags
