"""丰海厂商编解码器模块。"""

import configparser
import re
from pathlib import Path

from highway_sdk.core.codec import BaseCodec
from highway_sdk.core.exceptions import DeviceOperationError

from ..tags import BrightnessTags, ItemTags, OperationTags, PlayTags, WindowTags
from .spec import ENCODING, ResultCode, What


class FengHaiCodec(BaseCodec):
    """丰海VMS编解码器。"""

    CONTENT_PATTERN = re.compile(r"<(.*)>", re.DOTALL)

    @classmethod
    def _is_ok(cls, data: bytes) -> bool:
        """检查返回是否成功。"""
        return data.startswith(ResultCode.SUCCESS.value)

    @classmethod
    def _parse_play_item(cls, play_item: str) -> ItemTags:
        """解析播放项字符串。"""
        fields = play_item.split(",")
        tags = ItemTags()
        tags.media = fields[3] if len(fields) > 3 else ""
        tags.duration = int(int(fields[0]) * 0.01) if len(fields) > 0 else 0
        tags.screen_in_mode = int(fields[1]) if len(fields) > 1 else 0
        tags.play_speed = int(fields[2]) if len(fields) > 2 else 0
        return tags

    @classmethod
    def _parse_play_list(cls, play_list: str) -> PlayTags:
        """解析播放列表。"""
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

    @classmethod
    @BaseCodec.register(What.GET_BRIGHTNESS_AND_MODE)
    def decode_get_brightness(cls, data: bytes) -> BrightnessTags:
        """解码亮度和模式响应。"""
        if not cls._is_ok(data):
            raise DeviceOperationError("Failed to get brightness and mode")

        max_brightness = 31
        tags = BrightnessTags()
        tags.mode = int(chr(data[1]))
        tags.brightness = round(int(data[-2:].decode("ascii")) / max_brightness * 100)
        return tags

    @classmethod
    @BaseCodec.register(What.GET_PLAY_ITEM)
    def decode_get_play_item(cls, data: bytes) -> ItemTags:
        """解码获取播放项响应。"""
        data_str = data.decode(ENCODING)
        tags = ItemTags()
        ret = cls.CONTENT_PATTERN.search(data_str[15:])
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

    @classmethod
    @BaseCodec.register(What.DOWNLOAD_FILE)
    def decode_download_file(cls, data: bytes) -> PlayTags:
        """解码下载文件响应。"""
        if not cls._is_ok(data):
            raise DeviceOperationError("Failed to get play list")

        sep = data.find(b"+")
        if sep < 0:
            raise DeviceOperationError("Invalid download response: missing '+' separator")
        return cls._parse_play_list(data[sep + 5 :].decode(ENCODING))

    @classmethod
    @BaseCodec.register(What.SET_BRIGHTNESS)
    def decode_set_brightness(cls, data: bytes) -> OperationTags:
        """解码设置亮度响应。"""
        if not cls._is_ok(data):
            raise DeviceOperationError("Failed to set brightness")
        return OperationTags(is_ok=True)

    @classmethod
    @BaseCodec.register(What.UPLOAD_FILE)
    def decode_upload_file(cls, data: bytes) -> OperationTags:
        """解码上传文件响应。"""
        if not cls._is_ok(data):
            raise DeviceOperationError("Failed to upload file")
        return OperationTags(is_ok=True)
