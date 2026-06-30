"""电明厂商编解码器模块。"""

import configparser
import re
from functools import lru_cache

from highway_sdk.core.codec import BaseCodec
from highway_sdk.core.exceptions import DeviceOperationError, ProtocolParsingError

from ..tags import (
    BrightnessMode,
    BrightnessTags,
    ItemTags,
    MediaTags,
    OperationTags,
    PlayTags,
    WindowTags,
)
from .spec import ENCODING, ResultCode, What


class DianMingCodec(BaseCodec):
    """电明VMS编解码器。"""

    # (pattern, field_name, cast, size_group) — size_group: 若为 int 则提取该组为 font_size
    _MEDIA_PATTERNS: tuple[tuple[re.Pattern, str, type | None, int | None], ...] = (
        (re.compile(r"\\T(\d{12})"), "font_color", None, None),
        (re.compile(r"\\F([a-zA-Z])(\d{4})"), "font", None, 2),
        (re.compile(r"\\K(\d{12})"), "background_color", None, None),
        (re.compile(r"\\M(\d{2})"), "word_space", int, None),
        (re.compile(r"\\B(\d{3})"), "bmp", None, None),
        (re.compile(r"\\J(\d{3})"), "jpg", None, None),
        (re.compile(r"\\G(\d{3})"), "gif", None, None),
        (re.compile(r"\\P(\d{3})"), "png", None, None),
    )
    _TEXT_PATTERN = re.compile(r"\\W(.+)")

    @classmethod
    def _is_ok(cls, data: bytes) -> bool:
        """检查返回是否成功。"""
        return data.startswith(ResultCode.SUCCESS.value)

    @classmethod
    def _parse_media(cls, media: str) -> MediaTags:
        """解析媒体字符串。"""
        tags = MediaTags(media=media)
        remaining = media

        for pattern, field, cast, size_group in cls._MEDIA_PATTERNS:
            ret = pattern.search(remaining)
            if ret:
                value = ret.group(1)
                setattr(tags, field, cast(value) if cast else value)
                if size_group:
                    tags.font_size = int(ret.group(size_group))
                start, end = ret.span()
                remaining = remaining[:start] + remaining[end:]

        ret = cls._TEXT_PATTERN.search(remaining)
        if ret:
            tags.text = ret.group(1)

        return tags

    @classmethod
    def _split_media(cls, media: str) -> list[str]:
        """按 \\C 分割多媒体字符串。"""
        parts = media.split("\\C")
        return [f"\\C{p}" for p in parts if p.strip()]

    @classmethod
    def _parse_now_play_item(cls, data: bytes) -> ItemTags:
        """解析当前播放项。"""
        tags = ItemTags(
            index=data[0:3].decode("ascii", errors="ignore"),
            duration=int(data[3:8].decode("ascii")),
            screen_in_mode=int(data[8:10].decode("ascii")),
            play_effect=int(data[10:12].decode("ascii")),
            screen_out_mode=int(data[12:14].decode("ascii")),
            play_speed=int(data[14:16].decode("ascii")),
        )
        tags.media = data[16:].decode(ENCODING, errors="ignore")
        for media in cls._split_media(tags.media):
            tags.media_list.append(cls._parse_media(media))
        return tags

    @classmethod
    def _parse_play_item(cls, play_item: str) -> ItemTags:
        """解析播放项字符串。"""
        fields = play_item.split(",")
        tags = ItemTags(
            media=fields[5],
            duration=int(fields[0]),
            screen_in_mode=int(fields[1]),
            play_effect=int(fields[2]),
            screen_out_mode=int(fields[3]),
            play_speed=int(fields[4]),
        )
        for media in cls._split_media(tags.media):
            tags.media_list.append(cls._parse_media(media))
        return tags

    @classmethod
    def _parse_play_list(cls, play_list: str) -> PlayTags:
        """解析播放列表。"""
        lines = play_list.splitlines()
        fixed_play = "\r\n".join(line.replace("\n", "\\n") for line in lines)

        parser = configparser.ConfigParser()
        parser.read_string(fixed_play)

        section = "PLAYLIST"
        window = WindowTags()
        for i in range(int(parser.get(section, "item_no"))):
            window.items.append(cls._parse_play_item(parser.get(section, f"item{i:03d}")))

        return PlayTags(windows=[window])

    @classmethod
    @lru_cache
    @BaseCodec.register(What.GET_BRIGHTNESS_AND_MODE_RESP)
    def decode_get_brightness(cls, data: bytes) -> BrightnessTags:
        """解码亮度和模式响应。

        数据域（ASCII）：[0:2]目的 [2:4]源 [4:6]指令 [6:8]红 [8:10]绿 [10:12]蓝 [12:14]当前亮度
        """
        max_brightness = 0x31  # 49
        red = data[6:8].decode("ascii")
        if red == "FF":
            mode = BrightnessMode.AUTO
            current = int(data[12:14].decode("ascii"), 16)
        else:
            mode = BrightnessMode.MANUAL
            current = int(red, 16)
        return BrightnessTags(mode=mode, brightness=round(current / max_brightness * 100))

    @classmethod
    @lru_cache
    @BaseCodec.register(What.GET_PLAY_ITEM_RESP)
    def decode_get_play_item(cls, data: bytes) -> ItemTags:
        """解码获取播放项响应。"""
        return cls._parse_now_play_item(data)

    @classmethod
    @lru_cache
    @BaseCodec.register(What.GET_PLAY_LIST_RESP)
    def decode_get_play_list(cls, data: bytes) -> PlayTags:
        """解码获取播放列表响应。"""
        pos = data.find(b"+")
        if pos < 0:
            raise ProtocolParsingError("Invalid play list data format")
        content = data[pos + 19 :].decode(ENCODING, errors="ignore")
        return cls._parse_play_list(content)

    @classmethod
    @lru_cache
    @BaseCodec.register(What.SET_PLAY_LIST_AND_PLAY_RESP)
    def decode_set_play_list(cls, data: bytes) -> OperationTags:
        """解码设置播放列表响应。"""
        if not cls._is_ok(data):
            raise DeviceOperationError("Failed to set play list")
        return OperationTags(is_ok=True)

    @classmethod
    @lru_cache
    @BaseCodec.register(What.SET_BRIGHTNESS_OR_MODE_RESP)
    def decode_set_brightness(cls, data: bytes) -> OperationTags:
        """解码设置亮度或模式响应。"""
        if not cls._is_ok(data):
            raise DeviceOperationError("Failed to set brightness or mode")
        return OperationTags(is_ok=True)
