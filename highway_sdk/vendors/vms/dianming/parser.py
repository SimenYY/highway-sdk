"""点明厂商解析器模块。

该模块提供了点明VMS设备的响应数据解析功能。
"""

from functools import lru_cache

from highway_sdk.core.exceptions import (
    DeviceOperationError,
    ProtocolParsingError,
)
from highway_sdk.vendors.vms._base import BaseParser
from highway_sdk.vendors.vms._tags import ItemTags

from .media import PlayParser
from .spec import ResultCode, What


class Parser(BaseParser):
    """点明VMS解析器。

    继承自BaseParser，提供点明厂商特定的解析功能。
    """

    @classmethod
    def _is_ok(cls, data: bytes):
        """检查返回是否成功。

        Args:
            data: 返回的数据。

        Returns:
            bool: 是否成功。
        """
        return data.startswith(ResultCode.SUCCESS.value)


@lru_cache
@Parser.register(What.GET_PLAY_ITEM_RESP)
def _parse_get_play_item(data: bytes):
    """解析获取播放项响应。

    Args:
        data: 响应数据。

    Returns:
        ItemTags: 播放项标签。

    Raises:
        DeviceOperationError: 获取播放项失败。
    """
    tags = ItemTags()
    if Parser._is_ok(data):
        tags.text = data[1:].decode("gbk", errors="ignore")
    else:
        raise DeviceOperationError("Failed to get play item")
    return tags


@lru_cache
@Parser.register(What.GET_PLAY_LIST_RESP)
def _parse_get_play_list(data: bytes):
    """解析获取播放列表响应。

    Args:
        data: 响应数据。

    Returns:
        PlayBuilder: 播放列表建造器。

    Raises:
        DeviceOperationError: 获取播放列表失败。
        ProtocolParsingError: 播放列表数据格式无效。
    """
    if not Parser._is_ok(data):
        raise DeviceOperationError("Failed to get play list")

    content_start = data.find(b"+") + 4 + 1
    if content_start < 5:
        raise ProtocolParsingError("Invalid play list data format")

    content = data[content_start:].decode("gbk", errors="ignore")
    return PlayParser.parse(content).build()


@lru_cache
@Parser.register(What.SET_PLAY_LIST_AND_PLAY_RESP)
def _parse_set_play_list(data: bytes):
    """解析设置播放列表响应。

    Args:
        data: 响应数据。

    Returns:
        dict: 包含状态信息的字典。

    Raises:
        DeviceOperationError: 设置播放列表失败。
    """
    if not Parser._is_ok(data):
        raise DeviceOperationError("Failed to set play list")
    return {"status": "success"}
