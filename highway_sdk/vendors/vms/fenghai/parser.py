"""丰海厂商解析器模块。

该模块提供了丰海VMS设备的响应数据解析功能。
"""

import re
from pathlib import Path

from highway_sdk.core.exceptions import (
    DeviceOperationError,
)
from highway_sdk.vendors.vms._base import BaseParser
from highway_sdk.vendors.vms._tags import BrightnessTags, ItemTags
from highway_sdk.vendors.vms.sansi.parser import Parser as SansiParser

from .spec import ENCODING, ResultCode, What

__all__ = ["Parser"]


class Parser(BaseParser):
    """丰海VMS解析器。

    继承自BaseParser，提供丰海厂商特定的解析功能。
    """

    CONTENT_PATTERN = re.compile(r"<(.*)>", re.DOTALL)

    @classmethod
    def _parse_play_list(cls, play_list: str):
        """解析播放列表。

        Args:
            play_list: 播放列表字符串。

        Returns:
            PlayBuilder: 播放列表建造器。
        """
        return SansiParser._parse_play_list(play_list)

    @classmethod
    def _is_ok(cls, data: bytes):
        """检查返回是否成功。

        Args:
            data: 返回的数据。

        Returns:
            bool: 是否成功。
        """
        return data.startswith(ResultCode.SUCCESS.value)


@Parser.register(What.GET_PLAY_ITEM)
def _parse_get_play_item(data: bytes):
    """解析获取播放项响应。

    Args:
        data: 响应数据。

    Returns:
        ItemTags: 播放项标签。
    """
    data_str = data.decode(ENCODING)
    tags = ItemTags()
    ret = Parser.CONTENT_PATTERN.search(data_str[15:])
    if ret:
        content = str(ret.group(1))
        if "." in content:
            tags.image_name = Path(content).stem
            tags.image_type = Path(content).suffix
        else:
            tags.text = content

    tags.duration = int(int(data_str[3:8]) * 0.01)
    tags.screen_in_mode = int(data_str[8:10])
    tags.index = data_str[0:3]
    return tags


@Parser.register(What.DOWNLOAD_FILE)
def _parse_download_file(data: bytes):
    """解析下载文件响应。

    Args:
        data: 响应数据。

    Returns:
        PlayBuilder: 播放列表建造器。

    Raises:
        DeviceOperationError: 获取播放列表失败。
    """
    if not Parser._is_ok(data):
        raise DeviceOperationError("Failed to get play list")

    return Parser._parse_play_list(data[(data.find(b"+") + 4 + 1) :].decode(ENCODING))


@Parser.register(What.UPLOAD_FILE)
def _parse_upload_file(data: bytes):
    """解析上传文件响应。

    Args:
        data: 响应数据。

    Raises:
        DeviceOperationError: 上传文件失败。
    """
    if not Parser._is_ok(data):
        raise DeviceOperationError("Failed to upload file")


@Parser.register(What.GET_BRIGHTNESS_AND_MODE)
def _parse_brightness_and_mode(data: bytes):
    """解析亮度和播放模式响应。

    Args:
        data: 亮度和播放模式数据。

    Returns:
        BrightnessTags: 亮度和播放模式标签。

    Raises:
        DeviceOperationError: 获取亮度和模式失败。
    """
    if not Parser._is_ok(data):
        raise DeviceOperationError("Failed to get brightness and mode")

    max_brightness = 31
    tags = BrightnessTags()
    tags.mode = int(chr(data[1]))
    tags.brightness = round(int(data[-2:].decode("ascii")) / max_brightness * 100)
    return tags
