from calendar import c
import configparser
import re
from highway_sdk.core.interface import BaseMessageChainParser
from highway_sdk.driver.vms.tags import ItemTags, WindowTags, PlayTags, BrightnessTags
from .spec import SansiWhat, SansiFrameResp, ENCODING


class SanSiMessageParser(BaseMessageChainParser):
    frame = SansiFrameResp

    def parse(self, req_what: bytes, frame: SansiFrameResp):
        if self._successor is not None:
            return self._successor.parse(req_what, frame)
        else:
            return frame

    def deserialize(self, message: bytes) -> SansiFrameResp:
        return SansiFrameResp.unpack(message)


class SanSiGetItemParser(SanSiMessageParser):
    XY_PATTERN = re.compile(r"\\C(\d{3})(\d{3})")
    COLOR_PATTERN = re.compile(r"\\c(\d{12})")
    BG_COLOR_PATTERN = re.compile(r"\\b(\d{12})")
    WORD_SPACE_PATTERN = re.compile(r"\\S(\d{2})")
    FONT_PATTERN = re.compile(r"\\f([a-zA-Z])(\d{4})")
    BMP_PATTERN = re.compile(r"\\B(\d{3})")
    JPG_PATTERN = re.compile(r"\\J(\d{3})")
    PNG_PATTERN = re.compile(r"\\P(\d{3})")
    GIF_PATTERN = re.compile(r"\\G(\d{3})")

    def parse(self, req_what: bytes, frame: SansiFrameResp):
        if req_what == SansiWhat.GET_ITEM:
            data = frame.data.decode(ENCODING)
            tags = self._parse_media(data[15:])

            tags.duration = int(int(data[3:8]) * 0.01)
            tags.screen_in = str(int(data[8:10]))
            tags.index = data[0:3]
            return tags
        elif self._successor is not None:
            return self._successor.parse(req_what, frame)
        else:
            return frame

    @classmethod
    def _parse_item(cls, item: str) -> ItemTags:
        fields = item.split(",")
        tags = cls._parse_media(fields[3])
        tags.duration = int(int(fields[0]) / 100)
        tags.screen_in = fields[1]
        tags.play_speed = int(fields[2])
        tags.content = item
        return tags

    @classmethod
    def _parse_media(cls, media: str) -> ItemTags:
        tags = ItemTags()
        tags.meida = media
        remaining = tags.meida
        res = cls.XY_PATTERN.search(remaining)
        if res:
            start, end = res.span()
            remaining = remaining[:start] + remaining[end:]

        res = cls.COLOR_PATTERN.search(remaining)
        if res:
            tags.font_color = res.group(1)
            start, end = res.span()
            remaining = remaining[:start] + remaining[end:]

        res = cls.FONT_PATTERN.search(remaining)
        if res:
            tags.font = res.group(1)
            tags.font_size = res.group(2)
            start, end = res.span()
            remaining = remaining[:start] + remaining[end:]

        res = cls.BG_COLOR_PATTERN.search(remaining)
        if res:
            tags.background_color = res.group(1)
            start, end = res.span()
            remaining = remaining[:start] + remaining[end:]

        res = cls.WORD_SPACE_PATTERN.search(remaining)
        if res:
            tags.word_space = int(res.group(1))
            start, end = res.span()
            remaining = remaining[:start] + remaining[end:]

        res = cls.BMP_PATTERN.search(remaining)
        if res:
            tags.bmp = res.group(1)
            start, end = res.span()
            remaining = remaining[:start] + remaining[end:]

        res = cls.JPG_PATTERN.search(remaining)
        if res:
            tags.jpg = res.group(1)
            start, end = res.span()
            remaining = remaining[:start] + remaining[end:]

        res = cls.GIF_PATTERN.search(remaining)
        if res:
            tags.gif = res.group(1)
            start, end = res.span()
            remaining = remaining[:start] + remaining[end:]

        res = cls.PNG_PATTERN.search(remaining)
        if res:
            tags.png = res.group(1)
            start, end = res.span()
            remaining = remaining[:start] + remaining[end:]

        tags.text = remaining

        return tags


class SanSiGetBrightnessParser(SanSiMessageParser):
    def parse(self, req_what: bytes, frame: SansiFrameResp):
        if req_what == SansiWhat.GET_BRIGHTNESS:
            return self._parse_brightness_and_mode(frame.data)

        elif self._successor is not None:
            return self._successor.parse(req_what, frame)
        else:
            return frame

    @classmethod
    def _parse_brightness_and_mode(cls, data: bytes):
        max_brightness = 31
        tags = BrightnessTags()
        tags.mode = int(chr(data[1]))
        tags.brightness = round(int(data[2:3].decode("ascii")) / max_brightness * 100)
        return tags


class SanSiDownloadFileParser(SanSiMessageParser):
    def parse(self, req_what: bytes, frame: SansiFrameResp):
        if req_what == SansiWhat.DOWNLOAD_FILE:
            return self._parse_play(frame.data.decode(ENCODING))
        elif self._successor is not None:
            return self._successor.parse(req_what, frame)
        else:
            return frame

    @classmethod
    def _parse_play(cls, play: str) -> PlayTags:
        tags = PlayTags()

        play_parser = configparser.ConfigParser()
        play_parser.read_string(play)
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

                    window_tags.items.append(
                        SanSiGetItemParser._parse_item(
                            play_parser.get(section, item_name)
                        )
                    )
                tags.windows.append(window_tags)
        else:
            window_tags = WindowTags()
            item_no = int(play_parser.get(section, "item_no"))
            for i in range(item_no):
                item_name = f"item{i}"
                window_tags.items.append(
                    SanSiGetItemParser._parse_item(play_parser.get(section, item_name))
                )
            tags.windows.append(window_tags)
        return tags
