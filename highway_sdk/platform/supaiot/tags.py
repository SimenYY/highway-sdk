import enum
from dataclasses import dataclass
from highway_sdk.core.interface import BaseTags
from highway_sdk.vendors.vms._tags import ItemTags, PlayTags, BrightnessTags


# ==============================================================================
# 枚举类
# ==============================================================================
class _FontEnum(enum.Enum):
    KAI_TI = ("k", "104")
    SONG_TI = ("s", "107")
    HEI_TI = ("h", "102")
    FANG_SONG = ("f", "115")

    @property
    def font(self):
        return self.value[0]

    @property
    def code(self):
        return self.value[1]

    @classmethod
    def get_font_by_code(cls, code: str):
        for member in cls:
            if member.code == code:
                return member.font

    @classmethod
    def get_code_by_font(cls, font: str):
        for member in cls:
            if member.font == font:
                return member.code


class _ColorEnum(enum.Enum):
    RED = ("255000000000", "1")
    YELLOW = ("255255000000", "2")
    GREEN = ("000255000000", "3")

    @property
    def code(self):
        return self.value[1]

    @property
    def rgba(self):
        return self.value[0]

    @classmethod
    def get_code_by_rgba(cls, rgba: str):
        for member in cls:
            if member.rgba == rgba:
                return member.code

    @classmethod
    def get_rgba_by_code(cls, code: str):
        for member in cls:
            if member.code == code:
                return member.rgba


# ==============================================================================
# 转换数据
# ==============================================================================
@dataclass
class _SupaiotItemTags(ItemTags):
    def to_dict(self):
        supaiot_tags = {
            "CT": self.text or self.image_name,
            "FC": _ColorEnum.get_code_by_rgba(str(self.font_color)),
            "SH": self.screen_in,
            "TI": self.duration,
            "FO": _FontEnum.get_code_by_font(str(self.font).lower()),
        }
        ret = super().to_dict()
        ret.update(supaiot_tags)
        return ret


@dataclass
class _SupaiotPlayTags(PlayTags):
    def to_dict(self):
        supaiot_tags = {}
        for window in self.windows:
            for i, item in enumerate(window.items):
                j = i + 1
                supaiot_tags.update(
                    {
                        f"FO{j}": _FontEnum.get_code_by_font(str(item.font).upper()),
                        f"FC{j}": _ColorEnum.get_code_by_rgba(str(item.font_color)),
                        f"ZCT{j}": item.text or item.image_name,
                        f"TI{j}": item.duration,
                        f"SH{j}": item.screen_in,
                    }
                )
        ret = super().to_dict()
        ret.update(supaiot_tags)
        return ret


@dataclass
class _SupaiotBrightnessTags(BrightnessTags):
    def to_dict(self):
        supaiot_tags = {"TGFK": self.brightness, "LDMS": self.mode}
        ret = super().to_dict()
        ret.update(supaiot_tags)
        return ret


def to_supaiot_tags(tags: BaseTags):
    """将SDK点位转为物联智控点位"""
    if isinstance(tags, ItemTags):
        return _SupaiotItemTags(**tags.__dict__).to_dict()
    elif isinstance(tags, PlayTags):
        return _SupaiotPlayTags(**tags.__dict__).to_dict()
    elif isinstance(tags, BrightnessTags):
        return _SupaiotBrightnessTags(**tags.__dict__).to_dict()
    else:
        raise ValueError(f"{type(tags)} is not supported")
