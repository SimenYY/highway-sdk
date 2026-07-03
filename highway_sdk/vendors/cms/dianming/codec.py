"""电明厂商编解码器模块。"""

import re

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

    @staticmethod
    def _to_int(value: bytes | str, field: str) -> int:
        """将字节或字符串转为 int，失败抛 ProtocolParsingError。"""
        try:
            return int(value)
        except (ValueError, TypeError) as e:
            raise ProtocolParsingError(f"Invalid {field}: {value!r}") from e

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
            duration=cls._to_int(data[3:8].decode("ascii"), "duration"),
            screen_in_mode=cls._to_int(data[8:10].decode("ascii"), "screen_in_mode"),
            play_effect=cls._to_int(data[10:12].decode("ascii"), "play_effect"),
            screen_out_mode=cls._to_int(data[12:14].decode("ascii"), "screen_out_mode"),
            play_speed=cls._to_int(data[14:16].decode("ascii"), "play_speed"),
        )
        tags.media = data[16:].decode(ENCODING, errors="ignore")
        for media in cls._split_media(tags.media):
            tags.media_list.append(cls._parse_media(media))
        return tags

    @classmethod
    def _parse_play_item(cls, play_item: str) -> ItemTags:
        """解析播放项字符串。"""
        fields = play_item.split(",")
        if len(fields) < 6:
            raise ProtocolParsingError(f"Invalid play item format: {play_item!r}")
        tags = ItemTags(
            media=fields[5],
            duration=cls._to_int(fields[0], "duration"),
            screen_in_mode=cls._to_int(fields[1], "screen_in_mode"),
            play_effect=cls._to_int(fields[2], "play_effect"),
            screen_out_mode=cls._to_int(fields[3], "screen_out_mode"),
            play_speed=cls._to_int(fields[4], "play_speed"),
        )
        for media in cls._split_media(tags.media):
            tags.media_list.append(cls._parse_media(media))
        return tags

    @classmethod
    def _parse_play_list(cls, play_list: str) -> PlayTags:
        """解析播放列表。

        格式: ITEM_NO=003\\r\\nITEM000=50,0,0,0,0,\\C000000\\Fs3232...
        """
        lines = play_list.splitlines()

        item_lines = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if line.startswith("ITEM_NO="):
                continue
            if line.startswith("ITEM"):
                item_lines.append(line)

        # 解析每个 ITEM
        window = WindowTags()
        for line in item_lines:
            eq_pos = line.find("=")
            if eq_pos < 0:
                continue
            play_item = line[eq_pos + 1 :]
            window.items.append(cls._parse_play_item(play_item))

        return PlayTags(windows=[window])

    @classmethod
    @BaseCodec.register(What.GET_BRIGHTNESS_AND_MODE_RESP)
    def decode_get_brightness(cls, data: bytes) -> BrightnessTags:
        """解码亮度和模式响应。

        数据域（ASCII）：[0:2]红 [2:4]绿 [4:6]蓝 [6]模式指示 [7]当前亮度值

        实际设备返回 8 字节数据，如 "FFFFFFI5" (0x46*6 + 0x49 + 0x35)
        - RGB 均为 "FF" 表示自动模式
        - data[6] 为模式指示字节 (0x49)
        - data[7] 为当前亮度值（原始字节，0-255）
        """
        red = data[0:2].decode("ascii", errors="ignore")
        if red == "FF":
            mode = BrightnessMode.AUTO
        else:
            mode = BrightnessMode.MANUAL

        # data[7] 为原始字节值，截断到 BrightnessTags.brightness 范围 0-100
        brightness = min(data[7], 100)

        return BrightnessTags(mode=mode, brightness=brightness)

    @classmethod
    @BaseCodec.register(What.GET_PLAY_ITEM_RESP)
    def decode_get_play_item(cls, data: bytes) -> ItemTags:
        """解码获取播放项响应。"""
        return cls._parse_now_play_item(data)

    @classmethod
    @BaseCodec.register(What.GET_PLAY_LIST_RESP)
    def decode_get_play_list(cls, data: bytes) -> PlayTags:
        """解码获取播放列表响应。

        数据域格式: +00000000play00.lst[PLAYLIST]\\r\\nITEM_NO=003\\r\\n...
        或: +00000000play00.lst\\r\\nITEM_NO=003\\r\\n...
        """
        # 查找 ITEM_NO= 标记
        marker = b"ITEM_NO="
        pos = data.find(marker)
        if pos < 0:
            raise ProtocolParsingError("Invalid play list data format: missing ITEM_NO marker")

        # 从 ITEM_NO= 开始提取内容
        content = data[pos:].decode(ENCODING, errors="ignore")
        return cls._parse_play_list(content)

    @classmethod
    @BaseCodec.register(What.SET_PLAY_LIST_AND_PLAY_RESP)
    def decode_set_play_list(cls, data: bytes) -> OperationTags:
        """解码设置播放列表响应。"""
        if not cls._is_ok(data):
            raise DeviceOperationError("Failed to set play list")
        return OperationTags(is_ok=True)

    @classmethod
    @BaseCodec.register(What.SET_BRIGHTNESS_OR_MODE_RESP)
    def decode_set_brightness(cls, data: bytes) -> OperationTags:
        """解码设置亮度或模式响应。"""
        if not cls._is_ok(data):
            raise DeviceOperationError("Failed to set brightness or mode")
        return OperationTags(is_ok=True)
