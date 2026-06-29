import configparser
import re
from functools import lru_cache

from highway_sdk.core.exceptions import (
    DeviceOperationError,
    ProtocolNotSupportedError,
    ProtocolParsingError,
)
from highway_sdk.vendors.vms._base import BaseParser
from highway_sdk.vendors.vms._tags import (
    BrightnessTags,
    ItemTags,
    PlayTags,
    WindowTags,
)

from .spec import ENCODING, Frame, What


class Parser(BaseParser):
    XY_PATTERN = re.compile(r"\\C(\d{3})(\d{3})")
    COLOR_PATTERN = re.compile(r"\\c(\d{12})")
    BG_COLOR_PATTERN = re.compile(r"\\b(\d{12})")
    WORD_SPACE_PATTERN = re.compile(r"\\S(\d{2})")
    FONT_PATTERN = re.compile(r"\\f([a-zA-Z])(\d{4})")
    BMP_PATTERN = re.compile(r"\\B(\d{3})")
    JPG_PATTERN = re.compile(r"\\J(\d{3})")
    PNG_PATTERN = re.compile(r"\\P(\d{3})")
    GIF_PATTERN = re.compile(r"\\G(\d{3})")

    @classmethod
    def parse(cls, what: What, frame: Frame):
        try:
            return cls._parsers[what](frame.data)
        except KeyError as e:
            raise ProtocolNotSupportedError(f"Unsupported what: {e}") from e
        except DeviceOperationError:
            raise
        except Exception as e:
            raise ProtocolParsingError(f"Failed to parse frame: {e}") from e

    @classmethod
    def _parse_media(cls, data_str: str) -> ItemTags:
        tags = ItemTags()
        tags.media = data_str
        remaining = tags.media
        ret = cls.XY_PATTERN.search(remaining)
        if ret:
            start, end = ret.span()
            remaining = remaining[:start] + remaining[end:]

        ret = cls.COLOR_PATTERN.search(remaining)
        if ret:
            tags.font_color = ret.group(1)
            start, end = ret.span()
            remaining = remaining[:start] + remaining[end:]

        ret = cls.FONT_PATTERN.search(remaining)
        if ret:
            tags.font = ret.group(1)
            tags.font_size = int(ret.group(2))
            start, end = ret.span()
            remaining = remaining[:start] + remaining[end:]

        ret = cls.BG_COLOR_PATTERN.search(remaining)
        if ret:
            tags.background_color = ret.group(1)
            start, end = ret.span()
            remaining = remaining[:start] + remaining[end:]

        ret = cls.WORD_SPACE_PATTERN.search(remaining)
        if ret:
            tags.word_space = int(ret.group(1))
            start, end = ret.span()
            remaining = remaining[:start] + remaining[end:]

        ret = cls.BMP_PATTERN.search(remaining)
        if ret:
            tags.bmp = ret.group(1)
            start, end = ret.span()
            remaining = remaining[:start] + remaining[end:]

        ret = cls.JPG_PATTERN.search(remaining)
        if ret:
            tags.jpg = ret.group(1)
            start, end = ret.span()
            remaining = remaining[:start] + remaining[end:]

        ret = cls.GIF_PATTERN.search(remaining)
        if ret:
            tags.gif = ret.group(1)
            start, end = ret.span()
            remaining = remaining[:start] + remaining[end:]

        ret = cls.PNG_PATTERN.search(remaining)
        if ret:
            tags.png = ret.group(1)
            start, end = ret.span()
            remaining = remaining[:start] + remaining[end:]

        tags.text = remaining
        return tags

    @classmethod
    def _parse_play_item(cls, play_item: str):
        fields = play_item.split(",")
        tags = cls._parse_media(fields[3])
        tags.duration = int(int(fields[0]) * 0.01)
        tags.screen_in_mode = int(fields[1])
        tags.play_speed = int(fields[2])
        tags.media = play_item
        return tags

    @classmethod
    def _parse_brightness_and_mode(cls, data: bytes) -> BrightnessTags:
        max_brightness = 31
        tags = BrightnessTags()
        tags.mode = int(chr(data[1]))
        tags.brightness = round(int(data[2:3].decode("ascii")) / max_brightness * 100)
        return tags

    @classmethod
    def _parse_play_list(cls, play_list: str) -> PlayTags:
        tags = PlayTags()

        lines = play_list.split("\r\n")
        fixed_play = "\r\n".join([line.replace("\n", "\\n") for line in lines])

        play_parser = configparser.ConfigParser()
        play_parser.read_string(fixed_play)

        section = "playlist"
        if play_parser.has_option(section, "nwindows"):
            n_windows = int(play_parser.get(section, "nwindows"))
            for i in range(n_windows):
                window_tags = WindowTags()
                window_tags.x = int(play_parser.get(section, f"windows{i}_x"))
                window_tags.y = int(play_parser.get(section, f"windows{i}_y"))
                window_tags.w = int(play_parser.get(section, f"windows{i}_w"))
                window_tags.h = int(play_parser.get(section, f"windows{i}_h"))
                if i == 0:
                    item_no = int(play_parser.get(section, "item_no"))
                    item_name_prefix = "item"
                else:
                    item_no = int(play_parser.get(section, f"windows{i}_item_no"))
                    item_name_prefix = f"windows{i}_item"
                for j in range(item_no):
                    item_name = f"{item_name_prefix}{j}"
                    window_tags.items.append(cls._parse_play_item(play_parser.get(section, item_name)))
                tags.windows.append(window_tags)
        else:
            window_tags = WindowTags()
            item_no = int(play_parser.get(section, "item_no"))
            for i in range(item_no):
                item_name = f"item{i}"
                window_tags.items.append(cls._parse_play_item(play_parser.get(section, item_name)))
            tags.windows.append(window_tags)
        return tags


@lru_cache
@Parser.register(What.GET_PLAY_ITEM)
def _parse_get_play_item(data: bytes):
    """解析获取播放项响应"""
    data_str = data.decode(ENCODING)
    tags = Parser._parse_media(data_str[15:])
    tags.duration = int(int(data_str[3:8]) * 0.01)
    tags.screen_in_mode = int(data_str[8:10])
    tags.index = data_str[0:3]
    return tags


@lru_cache
@Parser.register(What.GET_BRIGHTNESS_AND_MODE)
def _parse_get_brightness_and_mode(data: bytes):
    """解析获取亮度和模式响应"""
    return Parser._parse_brightness_and_mode(data)


@lru_cache
@Parser.register(What.UPLOAD_FILE)
def _parse_upload_file(data: bytes):
    """解析上传播放表响应"""
    return Parser._parse_play_list(data.decode(ENCODING))


@lru_cache
@Parser.register(What.DOWNLOAD_FILE)
def _parse_download_file(data: bytes):
    """解析下载播放表响应"""
    return Parser._parse_play_list(data.decode(ENCODING))
