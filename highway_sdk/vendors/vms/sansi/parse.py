import configparser
import re
from highway_sdk.vendors.vms._tags import ItemTags, WindowTags, PlayTags, BrightnessTags
from .spec import SansiRespFrame, ENCODING, SansiWhatEnum


class SansiMessageParser:
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
    def parse(cls, req_what: bytes, message: bytes):
        frame = SansiRespFrame.unpack(message)

        match req_what:
            case SansiWhatEnum.GET_BRIGHTNESS_AND_MODE.value:
                return cls._extract_brightness_and_mode_tags(frame.data)
            case SansiWhatEnum.GET_ITEM.value:
                return cls._extract_item_tags(frame.data)
            case SansiWhatEnum.UPLOAD_FILE.value:
                return cls._extract_play_tags(frame.data)
            case _:
                raise ValueError(f"{req_what} is not supported")

    @classmethod
    def _extract_item_tags(cls, data: bytes):
        data_str = data.decode(ENCODING)
        tags = cls._parse_media(data_str[15:])

        tags.duration = int(int(data_str[3:8]) * 0.01)
        tags.screen_in = str(int(data_str[8:10]))
        tags.index = data_str[0:3]
        return tags

    @classmethod
    def _extract_brightness_and_mode_tags(cls, data: bytes):
        return cls._parse_brightness_and_mode(data)

    @classmethod
    def _extract_play_tags(cls, data: bytes):
        return cls._parse_play(data.decode(ENCODING))

    @classmethod
    def _parse_item(cls, item: str):
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
                        cls._parse_item(play_parser.get(section, item_name))
                    )
                tags.windows.append(window_tags)
        else:
            window_tags = WindowTags()
            item_no = int(play_parser.get(section, "item_no"))
            for i in range(item_no):
                item_name = f"item{i}"
                window_tags.items.append(
                    cls._parse_item(play_parser.get(section, item_name))
                )
            tags.windows.append(window_tags)
        return tags

    @classmethod
    def _parse_brightness_and_mode(cls, data: bytes):
        max_brightness = 31
        tags = BrightnessTags()
        tags.mode = int(chr(data[1]))
        tags.brightness = round(int(data[2:3].decode("ascii")) / max_brightness * 100)
        return tags
