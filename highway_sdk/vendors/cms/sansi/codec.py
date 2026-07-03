"""三思厂商编解码器模块。"""

import configparser
import re

from highway_sdk.core.codec import BaseCodec
from highway_sdk.core.exceptions import DeviceOperationError

from .spec import ENCODING, ResultCode, What


class SanSiCodec(BaseCodec):
    """三思CMS编解码器。"""

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
    def _is_ok(cls, data: bytes) -> bool:
        """检查返回是否成功。"""
        return data.startswith(ResultCode.SUCCESS.value)

    @classmethod
    def _parse_media(cls, data_str: str) -> dict:
        """解析媒体字符串。"""
        result = {}
        result["media"] = data_str
        remaining = result["media"]

        ret = cls.XY_PATTERN.search(remaining)
        if ret:
            start, end = ret.span()
            remaining = remaining[:start] + remaining[end:]

        ret = cls.COLOR_PATTERN.search(remaining)
        if ret:
            result["font_color"] = ret.group(1)
            start, end = ret.span()
            remaining = remaining[:start] + remaining[end:]

        ret = cls.FONT_PATTERN.search(remaining)
        if ret:
            result["font"] = ret.group(1)
            result["font_size"] = int(ret.group(2))
            start, end = ret.span()
            remaining = remaining[:start] + remaining[end:]

        ret = cls.BG_COLOR_PATTERN.search(remaining)
        if ret:
            result["background_color"] = ret.group(1)
            start, end = ret.span()
            remaining = remaining[:start] + remaining[end:]

        ret = cls.WORD_SPACE_PATTERN.search(remaining)
        if ret:
            result["word_space"] = int(ret.group(1))
            start, end = ret.span()
            remaining = remaining[:start] + remaining[end:]

        ret = cls.BMP_PATTERN.search(remaining)
        if ret:
            result["bmp"] = ret.group(1)
            start, end = ret.span()
            remaining = remaining[:start] + remaining[end:]

        ret = cls.JPG_PATTERN.search(remaining)
        if ret:
            result["jpg"] = ret.group(1)
            start, end = ret.span()
            remaining = remaining[:start] + remaining[end:]

        ret = cls.GIF_PATTERN.search(remaining)
        if ret:
            result["gif"] = ret.group(1)
            start, end = ret.span()
            remaining = remaining[:start] + remaining[end:]

        ret = cls.PNG_PATTERN.search(remaining)
        if ret:
            result["png"] = ret.group(1)
            start, end = ret.span()
            remaining = remaining[:start] + remaining[end:]

        result["text"] = remaining
        return result

    @classmethod
    def _parse_play_item(cls, play_item: str) -> dict:
        """解析播放项字符串。"""
        fields = play_item.split(",")
        result = cls._parse_media(fields[3])
        result["duration"] = int(int(fields[0]) * 0.01)
        result["screen_in_mode"] = int(fields[1])
        result["play_speed"] = int(fields[2])
        result["media"] = play_item
        return result

    @classmethod
    def _parse_brightness_and_mode(cls, data: bytes) -> dict:
        """解析亮度和模式。"""
        max_brightness = 31
        result = {}
        result["mode"] = int(chr(data[1]))
        result["brightness"] = round(int(data[2:4].decode("ascii", errors="ignore")) / max_brightness * 100)
        return result

    @classmethod
    def _parse_play_list(cls, play_list: str) -> dict:
        """解析播放列表。"""
        result = {"windows": []}

        lines = play_list.split("\r\n")
        fixed_play = "\r\n".join([line.replace("\n", "\\n") for line in lines])

        play_parser = configparser.ConfigParser()
        play_parser.read_string(fixed_play)

        section = "playlist"
        if play_parser.has_option(section, "nwindows"):
            n_windows = int(play_parser.get(section, "nwindows"))
            for i in range(n_windows):
                window = {}
                window["x"] = int(play_parser.get(section, f"windows{i}_x"))
                window["y"] = int(play_parser.get(section, f"windows{i}_y"))
                window["w"] = int(play_parser.get(section, f"windows{i}_w"))
                window["h"] = int(play_parser.get(section, f"windows{i}_h"))
                if i == 0:
                    item_no = int(play_parser.get(section, "item_no"))
                    item_name_prefix = "item"
                else:
                    item_no = int(play_parser.get(section, f"windows{i}_item_no"))
                    item_name_prefix = f"windows{i}_item"
                window["items"] = []
                for j in range(item_no):
                    item_name = f"{item_name_prefix}{j}"
                    window["items"].append(cls._parse_play_item(play_parser.get(section, item_name)))
                result["windows"].append(window)
        else:
            window = {}
            item_no = int(play_parser.get(section, "item_no"))
            window["items"] = []
            for i in range(item_no):
                item_name = f"item{i}"
                window["items"].append(cls._parse_play_item(play_parser.get(section, item_name)))
            result["windows"].append(window)
        return result

    @classmethod
    @BaseCodec.register(What.GET_PLAY_ITEM)
    def decode_get_play_item(cls, data: bytes) -> dict:
        """解码获取播放项响应。"""
        data_str = data.decode(ENCODING)
        result = cls._parse_media(data_str[15:])
        result["duration"] = int(int(data_str[3:8]) * 0.01)
        result["screen_in_mode"] = int(data_str[8:10])
        result["index"] = data_str[0:3]
        return result

    @classmethod
    @BaseCodec.register(What.GET_BRIGHTNESS_AND_MODE)
    def decode_get_brightness(cls, data: bytes) -> dict:
        """解码获取亮度和模式响应。"""
        return cls._parse_brightness_and_mode(data)

    @classmethod
    @BaseCodec.register(What.UPLOAD_FILE)
    def decode_upload_file(cls, data: bytes) -> dict:
        """解码上传文件响应。"""
        if not cls._is_ok(data):
            raise DeviceOperationError("Failed to upload file")
        return {"is_ok": True}

    @classmethod
    @BaseCodec.register(What.DOWNLOAD_FILE)
    def decode_download_file(cls, data: bytes) -> dict:
        """解码下载播放表响应。"""
        return cls._parse_play_list(data.decode(ENCODING))

    @classmethod
    @BaseCodec.register(What.SET_BRIGHTNESS)
    def decode_set_brightness(cls, data: bytes) -> dict:
        """解码设置亮度响应。"""
        if not cls._is_ok(data):
            raise DeviceOperationError("Failed to set brightness")
        return {"is_ok": True}
