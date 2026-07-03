"""显科厂商编解码器模块。"""

import configparser
import re

from highway_sdk.core.codec import BaseCodec
from highway_sdk.core.exceptions import DeviceOperationError

from ..tags import BrightnessTags, ItemTags, OperationTags, PlayTags, WindowTags
from .spec import ResultCode, What


class XianKeCodec(BaseCodec):
    """显科VMS编解码器。"""

    FONT_PATTERN = re.compile(r"\\F([a-zA-Z])(\d{2})")
    COLOR_PATTERN = re.compile(r"\\T(\d{12})")
    BMP_PATTERN = re.compile(r"\\I(\d{3})")
    GIF_PATTERN = re.compile(r"\\G(\d{3})")
    VIDEO_PATTERN = re.compile(r"\\V(\d{3})")
    BG_COLOR_PATTERN = re.compile(r"\\B(\d{12})")
    TEXT_PATTERN = re.compile(r"\\U(.*)")

    @classmethod
    def _is_ok(cls, data: bytes) -> bool:
        """检查返回是否成功。"""
        return data.startswith(ResultCode.SUCCESS.value)

    @classmethod
    def _parse_play_list(cls, play_list: str) -> PlayTags:
        """解析播放表。"""
        play_parser = configparser.ConfigParser()
        play_parser.read_string(play_list)
        section = "LIST"
        item_count = int(play_parser.get(section, "ItemCount"))
        play_tags = PlayTags()
        window_tags = WindowTags()
        for i in range(item_count):
            option = f"Item{i:02d}"
            item = play_parser.get(section, option)
            item_tags = cls._parse_play_item(item)
            window_tags.items.append(item_tags)
        play_tags.windows.append(window_tags)
        return play_tags

    @classmethod
    def _parse_play_item(cls, play_item: str) -> ItemTags:
        """解析播放项。"""
        fields = play_item.split(",")
        tags = cls._parse_media(fields[5])

        tags.duration = int(fields[0])
        tags.screen_in_mode = int(fields[1])
        tags.play_effect = int(fields[2])
        tags.screen_out_mode = int(fields[3])
        tags.play_speed = int(fields[4])

        return tags

    @classmethod
    def _parse_media(cls, media: str) -> ItemTags:
        """解析媒体字符串。"""
        tags = ItemTags()
        tags.media = media
        remaining = media

        # 字体
        ret = cls.FONT_PATTERN.search(remaining)
        if ret:
            tags.font = ret.group(1)
            tags.font_size = int(ret.group(2))
            start, end = ret.span()
            remaining = remaining[:start] + remaining[end:]

        # 字体颜色
        ret = cls.COLOR_PATTERN.search(remaining)
        if ret:
            tags.font_color = ret.group(1)
            start, end = ret.span()
            remaining = remaining[:start] + remaining[end:]

        # 背景颜色
        ret = cls.BG_COLOR_PATTERN.search(remaining)
        if ret:
            tags.background_color = ret.group(1)
            start, end = ret.span()
            remaining = remaining[:start] + remaining[end:]

        ret = cls.TEXT_PATTERN.search(remaining)
        if ret:
            text = ret.group(1)
            tags.text = text
            start, end = ret.span()
            remaining = remaining[:start] + remaining[end:]

        ret = cls.BMP_PATTERN.search(remaining)
        if ret:
            tags.bmp = ret.group(1)
            start, end = ret.span()
            remaining = remaining[:start] + remaining[end:]

        ret = cls.GIF_PATTERN.search(remaining)
        if ret:
            tags.gif = ret.group(1)
            start, end = ret.span()
            remaining = remaining[:start] + remaining[end:]

        ret = cls.VIDEO_PATTERN.search(remaining)
        if ret:
            tags.mpg = ret.group(1)

        return tags

    @classmethod
    @BaseCodec.register(What.GET_PLAY_ITEM)
    def decode_get_play_item(cls, data: bytes) -> ItemTags:
        """解码获取播放项响应。"""
        tags = ItemTags()
        if cls._is_ok(data):
            content = data[1:].decode("gbk", errors="ignore")
            tags.text = content
        else:
            raise DeviceOperationError("Failed to get item")
        return tags

    @classmethod
    @BaseCodec.register(What.GET_PLAY_LIST_NAME)
    def decode_get_play_list_name(cls, data: bytes) -> OperationTags:
        """解码获取播放列表响应。"""
        if not cls._is_ok(data):
            raise DeviceOperationError("Failed to get play list")

        return OperationTags(is_ok=True)

    @classmethod
    @BaseCodec.register(What.GET_BRIGHTNESS_AND_MODE)
    def decode_get_brightness(cls, data: bytes) -> BrightnessTags:
        """解码获取亮度响应。"""
        if not cls._is_ok(data):
            raise DeviceOperationError("Failed to get brightness")

        tags = BrightnessTags()
        if len(data) > 1:
            tags.brightness = int(data[1:].decode("gbk", errors="ignore"))
            tags.mode = 1  # 假设为手动模式
        return tags

    @classmethod
    @BaseCodec.register(What.UPLOAD_FILE)
    def decode_upload_file(cls, data: bytes) -> OperationTags:
        """解码上传文件响应。"""
        if not cls._is_ok(data):
            raise DeviceOperationError("Failed to upload file")
        return OperationTags(is_ok=True)

    @classmethod
    @BaseCodec.register(What.DOWNLOAD_FILE)
    def decode_download_file(cls, data: bytes) -> PlayTags:
        """解码下载文件响应。"""
        if not cls._is_ok(data):
            raise DeviceOperationError("Failed to download file")

        return cls._parse_play_list(data[1:].decode("gbk", errors="ignore"))

    @classmethod
    @BaseCodec.register(What.SELECT_PLAY_LIST)
    def decode_play_list(cls, data: bytes) -> OperationTags:
        """解码播放列表响应。"""
        if not cls._is_ok(data):
            raise DeviceOperationError("Failed to play list")
        return OperationTags(is_ok=True)
