"""丰海厂商编解码器模块。"""

import configparser
import re
from pathlib import Path

from highway_sdk.core.codec import BaseCodec
from highway_sdk.core.exceptions import DeviceOperationError

from .._base import parse_media
from .spec import ENCODING, ResultCode, What


class FengHaiCodec(BaseCodec):
    """丰海CMS编解码器。"""

    CONTENT_PATTERN = re.compile(r"<(.*)>", re.DOTALL)

    @classmethod
    def _is_ok(cls, data: bytes) -> bool:
        """检查返回是否成功。"""
        return data.startswith(ResultCode.SUCCESS.value)

    @classmethod
    def _parse_play_item(cls, play_item: str) -> dict:
        """解析播放项字符串。"""
        fields = play_item.split(",")
        result = parse_media(fields[3])
        result["duration"] = int(int(fields[0]) * 0.01)
        result["screen_in_mode"] = int(fields[1])
        result["play_speed"] = int(fields[2])
        result["media"] = play_item
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
    @BaseCodec.register(What.GET_BRIGHTNESS_AND_MODE)
    def decode_get_brightness(cls, data: bytes) -> dict:
        """解码亮度和模式响应。"""
        if not cls._is_ok(data):
            raise DeviceOperationError("Failed to get brightness and mode")

        max_brightness = 31
        mode = int(chr(data[1]))
        brightness = round(int(data[-2:].decode("ascii")) / max_brightness * 100)
        return {"mode": mode, "brightness": brightness}

    @classmethod
    @BaseCodec.register(What.GET_PLAY_ITEM)
    def decode_get_play_item(cls, data: bytes) -> dict:
        """解码获取播放项响应。"""
        data_str = data.decode(ENCODING)
        result = {}
        ret = cls.CONTENT_PATTERN.search(data_str[15:])
        if ret:
            content = str(ret.group(1))
            if "." in content:
                result["image_name"] = Path(content).stem
                result["image_type"] = Path(content).suffix
            else:
                result["text"] = content

        result["duration"] = int(int(data_str[3:8]) * 0.01)
        result["screen_in_mode"] = int(data_str[8:10])
        result["index"] = data_str[0:3]
        return result

    @classmethod
    @BaseCodec.register(What.DOWNLOAD_FILE)
    def decode_download_file(cls, data: bytes) -> dict:
        """解码下载文件响应。"""
        if not cls._is_ok(data):
            raise DeviceOperationError("Failed to get play list")

        sep = data.find(b"+")
        if sep < 0:
            raise DeviceOperationError("Invalid download response: missing '+' separator")
        return cls._parse_play_list(data[sep + 5 :].decode(ENCODING))

    @classmethod
    @BaseCodec.register(What.SET_BRIGHTNESS)
    def decode_set_brightness(cls, data: bytes) -> dict:
        """解码设置亮度响应。"""
        if not cls._is_ok(data):
            raise DeviceOperationError("Failed to set brightness")
        return {"is_ok": True}

    @classmethod
    @BaseCodec.register(What.UPLOAD_FILE)
    def decode_upload_file(cls, data: bytes) -> dict:
        """解码上传文件响应。"""
        if not cls._is_ok(data):
            raise DeviceOperationError("Failed to upload file")
        return {"is_ok": True}
