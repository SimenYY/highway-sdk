"""点明厂商解析器模块。

该模块提供了点明VMS设备的响应数据解析功能。
"""

import configparser
import re
from functools import lru_cache

from highway_sdk.core.exceptions import (
    DeviceOperationError,
    ProtocolParsingError,
)
from highway_sdk.vendors.vms._base import BaseParser
from highway_sdk.vendors.vms._tags import BrightnessTags, ItemTags, PlayTags, WindowTags

from .._tags import BrightnessMode, MediaTags
from .spec import Frame, ResultCode, What


class Parser(BaseParser):
    """点明VMS解析器。

    继承自BaseParser，提供点明厂商特定的解析功能。
    """

    XY_PATTERN = re.compile(r"\\C(\d{3})(\d{3})")
    BMP_PATTERN = re.compile(r"\\B(\d{3})")
    PNG_PATTERN = re.compile(r"\\P(\d{3})")
    JPG_PATTERN = re.compile(r"\\J(\d{3})")
    GIF_PATTERN = re.compile(r"\\G(\d{3})")
    TEXT_PATTERN = re.compile(r"\\W(.+)")
    PNG_PATTERN = re.compile(r"\\P(\d{3})")
    COLOR_PATTERN = re.compile(r"\\T(\d{12})")
    BG_COLOR_PATTERN = re.compile(r"\\K(\d{12})")
    WORD_SPACE_PATTERN = re.compile(r"\\M(\d{2})")
    FONT_PATTERN = re.compile(r"\\F([a-zA-Z])(\d{4})")

    @classmethod
    def _is_ok(cls, data: bytes):
        """检查返回是否成功。

        Args:
            data: 返回的数据。

        Returns:
            bool: 是否成功。
        """
        return data.startswith(ResultCode.SUCCESS.value)

    @classmethod
    def parse(cls, frame: Frame):
        return super().parse(frame)

    @classmethod
    def _parse_media(cls, media: str) -> MediaTags:
        media_tags = MediaTags()
        media_tags.media = media
        remaining = media_tags.media
        ret = cls.XY_PATTERN.search(remaining)
        if ret:
            start, end = ret.span()
            remaining = remaining[:start] + remaining[end:]
        ret = cls.COLOR_PATTERN.search(remaining)
        if ret:
            media_tags.font_color = ret.group(1)
            start, end = ret.span()
            remaining = remaining[:start] + remaining[end:]
            ret = cls.FONT_PATTERN.search(remaining)
        if ret:
            media_tags.font = ret.group(1)
            media_tags.font_size = int(ret.group(2))
            start, end = ret.span()
            remaining = remaining[:start] + remaining[end:]
        ret = cls.BG_COLOR_PATTERN.search(remaining)
        if ret:
            media_tags.background_color = ret.group(1)
            start, end = ret.span()
            remaining = remaining[:start] + remaining[end:]

        ret = cls.WORD_SPACE_PATTERN.search(remaining)
        if ret:
            media_tags.word_space = int(ret.group(1))
            start, end = ret.span()
            remaining = remaining[:start] + remaining[end:]

        ret = cls.BMP_PATTERN.search(remaining)
        if ret:
            media_tags.bmp = ret.group(1)
            start, end = ret.span()
            remaining = remaining[:start] + remaining[end:]

        ret = cls.JPG_PATTERN.search(remaining)
        if ret:
            media_tags.jpg = ret.group(1)
            start, end = ret.span()
            remaining = remaining[:start] + remaining[end:]

        ret = cls.GIF_PATTERN.search(remaining)
        if ret:
            media_tags.gif = ret.group(1)
            start, end = ret.span()
            remaining = remaining[:start] + remaining[end:]

        ret = cls.PNG_PATTERN.search(remaining)
        if ret:
            media_tags.png = ret.group(1)
            start, end = ret.span()
            remaining = remaining[:start] + remaining[end:]
        res = cls.TEXT_PATTERN.search(remaining)
        if res:
            media_tags.text = res.group(1)
        return media_tags

    @classmethod
    def _parse_play_item(cls, play_item: str) -> ItemTags:
        fields = play_item.split(",")
        # tags = cls._parse_media(fields[5])
        tags = ItemTags()
        tags.media = fields[5]
        tags.duration = int(fields[0])
        tags.screen_in_mode = int(fields[1])
        tags.play_effect = int(fields[2])
        tags.screen_out_mode = int(fields[3])
        tags.play_speed = int(fields[4])
        media_list = tags.media.split("\\C")
        media_list = ["\\C" + media for media in media_list if media.strip() != ""]

        for media in media_list:
            media_tags = cls._parse_media(media)
            tags.media_list.append(media_tags)

        return tags

    @classmethod
    def _parse_now_play_item(cls, data: bytes) -> ItemTags:
        tags = ItemTags()
        tags.index = data[0:3].decode("ascii", errors="ignore")
        tags.duration = int(data[3:8].decode("ascii"))
        tags.screen_in_mode = int(data[8:10].decode("ascii"))
        tags.play_effect = int(data[10:12].decode("ascii"))
        tags.screen_out_mode = int(data[12:14].decode("ascii"))
        tags.play_speed = int(data[14:16].decode("ascii"))
        tags.media = data[16:].decode("gbk", errors="ignore")

        # 判断是否多个媒体
        n = tags.media.count("\\C")
        if n > 1:
            media_list = tags.media.split("\\C")
            media_list = ["\\C" + media for media in media_list if media.strip() != ""]
        else:
            media_list = [tags.media]
        for media in media_list:
            media_tags = cls._parse_media(media)
            tags.media_list.append(media_tags)

        return tags

    @classmethod
    def _parse_play_list(cls, play_list: str) -> PlayTags:
        tags = PlayTags()
        lines = play_list.splitlines()
        fixed_play = "\r\n".join([line.replace("\n", "\\n") for line in lines])
        play_parser = configparser.ConfigParser()
        play_parser.read_string(fixed_play)
        section = "PLAYLIST"
        window_tags = WindowTags()
        item_no = int(play_parser.get(section, "item_no"))
        for i in range(item_no):
            item_name = f"item{i:03d}"
            window_tags.items.append(cls._parse_play_item(play_parser.get(section, item_name)))
        tags.windows.append(window_tags)

        return tags


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
    return Parser._parse_now_play_item(data)


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
    # if not Parser._is_ok(data):
    #     raise DeviceOperationError("Failed to get play list")

    content_start = data.find(b"+") + 19
    if content_start < 19:
        raise ProtocolParsingError("Invalid play list data format")

    content = data[content_start:].decode("gbk", errors="ignore")
    return Parser._parse_play_list(content)


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


@lru_cache
@Parser.register(What.GET_BRIGHTNESS_AND_MODE_RESP)
def _parse_get_brightness_and_mode(data: bytes):
    """解析获取亮度和控制亮度模式响应。

    Args:
        data: 响应数据。

    Returns:
        dict: 包含亮度和控制亮度模式的字典。

    Raises:
        DeviceOperationError: 获取亮度和控制亮度模式失败。
    """
    max_brightness = 31
    tags = BrightnessTags()

    value = int(data[6:8].decode("ascii"))
    tags.brightness = round(value / max_brightness * 100)

    tags.mode = BrightnessMode.AUTO if data[0] == b"f" else BrightnessMode.MANUAL

    return tags


@lru_cache
@Parser.register(What.SET_BRIGHTNESS_OR_MODE_RESP)
def _parse_set_brightness_or_mode(data: bytes):
    """解析设置亮度或控制亮度模式响应。

    Args:
        data: 响应数据。

    Returns:
        dict: 包含状态信息的字典。

    Raises:
        DeviceOperationError: 设置亮度或控制亮度模式失败。
    """
    if not Parser._is_ok(data):
        raise DeviceOperationError("Failed to set brightness or mode")
    return {"status": "success"}
