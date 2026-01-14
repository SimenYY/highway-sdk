import configparser
import re

from highway_sdk.core.exceptions import (
    DeviceOperationError,
)
from highway_sdk.vendors.vms._base import BaseParser
from highway_sdk.vendors.vms._tags import (
    BrightnessTags,
    ItemTags,
    OperationTags,
    PlayTags,
    WindowTags,
)

from .spec import ResultCode, What


class Parser(BaseParser):
    FONT_PATTERN = re.compile(r"\\F([a-zA-Z])(\d{2})")
    COLOR_PATTERN = re.compile(r"\\T(\d{12})")
    BMP_PATTERN = re.compile(r"\\I(\d{3})")
    GIF_PATTERN = re.compile(r"\\G(\d{3})")
    VIDEO_PATTERN = re.compile(r"\\V(\d{3})")
    BG_COLOR_PATTERN = re.compile(r"\\B(\d{12})")
    TEXT_PATTERN = re.compile(r"\\U(.*)")

    @classmethod
    def _is_ok(cls, data: bytes):
        """检查返回是否成功"""
        return data.startswith(ResultCode.SUCCESS.value)

    @classmethod
    def _parse_play_list(cls, play_list: str):
        """解析播放表

        播放表格式
        [LIST]
        ItemCount=002
        Item00=2,1,0,1,1,\\C000000\\Fs32\\T255000000000\\B000000000000\\U 深圳显科科技有限公司
        Item01=2,1,0,1,1,\\C000000\\Fs32\\T000255000000\\B000000000000\\U 深圳显科科技有限公司


        Args:
            play_list (str): _description_

        Returns:
            _type_: _description_
        """
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
    def _parse_play_item(cls, play_item: str):
        fields = play_item.split(",")
        tags = cls._parse_media(fields[5])

        tags.duration = int(fields[0])
        tags.screen_in_mode = int(fields[1])
        tags.play_effect = int(fields[2])
        tags.screen_out_mode = int(fields[3])
        tags.play_speed = int(fields[4])

        return tags

    @classmethod
    def _parse_media(cls, media: str):
        tags = ItemTags()
        tags.meida, remaining = media, media

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


@Parser.register(What.GET_PLAY_ITEM)
def _parse_get_play_item(data: bytes):
    """解析获取播放项响应"""
    tags = ItemTags()
    if Parser._is_ok(data):
        # 解析当前播放项，根据实际返回格式调整
        content = data[1:].decode("gbk", errors="ignore")
        tags.text = content
    else:
        raise DeviceOperationError("Failed to get item")
    return tags


@Parser.register(What.GET_PLAY_LIST_NAME)
def _parse_get_play_list_name(data: bytes):
    """解析获取播放列表响应"""
    if not Parser._is_ok(data):
        raise DeviceOperationError("Failed to get play list")

    return OperationTags(is_ok=True)


@Parser.register(What.GET_BRIGHTNESS_AND_MODE)
def _parse_get_brightness(data: bytes):
    """解析获取亮度响应"""
    if not Parser._is_ok(data):
        raise DeviceOperationError("Failed to get brightness")

    tags = BrightnessTags()
    # 假设数据格式为：状态码 + 亮度值
    if len(data) > 1:
        tags.brightness = int(data[1:].decode("gbk", errors="ignore"))
        tags.mode = 1  # 假设为手动模式
    return tags


@Parser.register(What.UPLOAD_FILE)
def _parse_upload_file(data: bytes):
    """解析上传文件响应"""
    if not Parser._is_ok(data):
        raise DeviceOperationError("Failed to upload file")
    return OperationTags(is_ok=True)


@Parser.register(What.DOWNLOAD_FILE)
def _parse_download_file(data: bytes):
    """解析下载文件响应"""
    if not Parser._is_ok(data):
        raise DeviceOperationError("Failed to download file")

    return Parser._parse_play_list(data[1:].decode("gbk", errors="ignore"))


@Parser.register(What.SELECT_PLAY_LIST)
def _parse_play_list(data: bytes):
    """解析播放列表响应"""
    if not Parser._is_ok(data):
        raise DeviceOperationError("Failed to play list")
    return OperationTags(is_ok=True)
