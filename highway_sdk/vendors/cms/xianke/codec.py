"""显科厂商编解码器模块。"""

import configparser
import re

from highway_sdk.core.codec import BaseCodec
from highway_sdk.core.exceptions import DeviceOperationError

from .spec import ResultCode, What


class XianKeCodec(BaseCodec):
    """显科CMS编解码器。"""

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
    def _parse_play_list(cls, play_list: str) -> dict:
        """解析播放表。"""
        play_parser = configparser.ConfigParser()
        play_parser.read_string(play_list)
        section = "LIST"
        item_count = int(play_parser.get(section, "ItemCount"))
        windows = []
        items = []
        for i in range(item_count):
            option = f"Item{i:02d}"
            item = play_parser.get(section, option)
            items.append(cls._parse_play_item(item))
        windows.append({"items": items})
        return {"windows": windows}

    @classmethod
    def _parse_play_item(cls, play_item: str) -> dict:
        """解析播放项。"""
        fields = play_item.split(",")
        result = cls._parse_media(fields[5])
        result["duration"] = int(fields[0])
        result["screen_in_mode"] = int(fields[1])
        result["play_effect"] = int(fields[2])
        result["screen_out_mode"] = int(fields[3])
        result["play_speed"] = int(fields[4])
        return result

    @classmethod
    def _parse_media(cls, media: str) -> dict:
        """解析媒体字符串。"""
        result: dict = {"media": media}
        remaining = media

        ret = cls.FONT_PATTERN.search(remaining)
        if ret:
            result["font"] = ret.group(1)
            result["font_size"] = int(ret.group(2))
            start, end = ret.span()
            remaining = remaining[:start] + remaining[end:]

        ret = cls.COLOR_PATTERN.search(remaining)
        if ret:
            result["font_color"] = ret.group(1)
            start, end = ret.span()
            remaining = remaining[:start] + remaining[end:]

        ret = cls.BG_COLOR_PATTERN.search(remaining)
        if ret:
            result["background_color"] = ret.group(1)
            start, end = ret.span()
            remaining = remaining[:start] + remaining[end:]

        ret = cls.TEXT_PATTERN.search(remaining)
        if ret:
            result["text"] = ret.group(1)
            start, end = ret.span()
            remaining = remaining[:start] + remaining[end:]

        ret = cls.BMP_PATTERN.search(remaining)
        if ret:
            result["bmp"] = ret.group(1)
            start, end = ret.span()
            remaining = remaining[:start] + remaining[end:]

        ret = cls.GIF_PATTERN.search(remaining)
        if ret:
            result["gif"] = ret.group(1)
            start, end = ret.span()
            remaining = remaining[:start] + remaining[end:]

        ret = cls.VIDEO_PATTERN.search(remaining)
        if ret:
            result["mpg"] = ret.group(1)

        return result

    @classmethod
    @BaseCodec.register(What.GET_PLAY_ITEM)
    def decode_get_play_item(cls, data: bytes) -> dict:
        """解码获取播放项响应。"""
        if cls._is_ok(data):
            content = data[1:].decode("gbk", errors="ignore")
            return {"text": content}
        raise DeviceOperationError("Failed to get item")

    @classmethod
    @BaseCodec.register(What.GET_PLAY_LIST_NAME)
    def decode_get_play_list_name(cls, data: bytes) -> dict:
        """解码获取播放列表响应。"""
        if not cls._is_ok(data):
            raise DeviceOperationError("Failed to get play list")
        return {"is_ok": True}

    @classmethod
    @BaseCodec.register(What.GET_BRIGHTNESS_AND_MODE)
    def decode_get_brightness(cls, data: bytes) -> dict:
        """解码获取亮度响应。"""
        if not cls._is_ok(data):
            raise DeviceOperationError("Failed to get brightness")
        brightness = int(data[1:].decode("gbk", errors="ignore")) if len(data) > 1 else 0
        return {"brightness": brightness, "mode": 1}

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
        """解码下载文件响应。

        响应格式：success_code(1B) + file_name_len(3B ASCII) + file_name + "0000"(4B) + INI 内容
        修复：必须跳过文件头前缀，仅解析尾部 INI 内容。
        """
        if not cls._is_ok(data):
            raise DeviceOperationError("Failed to download file")
        if len(data) < 8:
            raise DeviceOperationError("Invalid download response: too short")
        try:
            file_name_len = int(data[1:4].decode("ascii"))
        except ValueError as e:
            raise DeviceOperationError(f"Invalid file_name_len in download response: {e}") from e
        # 跳过 success_code(1) + file_name_len(3) + file_name + "0000"(4)
        sep = 4 + file_name_len + 4
        if len(data) < sep:
            raise DeviceOperationError("Invalid download response: truncated file header")
        return cls._parse_play_list(data[sep:].decode("gbk", errors="ignore"))

    @classmethod
    @BaseCodec.register(What.SELECT_PLAY_LIST)
    def decode_play_list(cls, data: bytes) -> dict:
        """解码播放列表响应。"""
        if not cls._is_ok(data):
            raise DeviceOperationError("Failed to play list")
        return {"is_ok": True}
