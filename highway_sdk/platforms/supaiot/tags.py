import enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from highway_sdk.core.base import BaseTags
from highway_sdk.vendors.vms._tags import (
    BrightnessTags,
    ItemTags,
    PlayTags,
)

__all__ = ["ControlVmsTagsModel", "convert"]


# ==============================================================================
# 枚举类
# ==============================================================================
class _FontEnum(enum.Enum):
    KAI_TI = ("k", 104)
    SONG_TI = ("s", 107)
    HEI_TI = ("h", 102)
    FANG_SONG = ("f", 115)

    @property
    def font(self):
        return self.value[0]

    @property
    def code(self):
        return self.value[1]

    @classmethod
    def get_font_by_code(cls, code: int):
        for member in cls:
            if member.code == code:
                return member.font

    @classmethod
    def get_code_by_font(cls, font: str):
        for member in cls:
            if member.font == font:
                return member.code


class _ColorEnum(enum.Enum):
    YELLOW = ("255255000000", 1)
    RED = ("255000000000", 2)
    GREEN = ("000255000000", 3)

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
    def get_rgba_by_code(cls, code: int):
        for member in cls:
            if member.code == code:
                return member.rgba


# ==============================================================================
# 状态点位
# ==============================================================================
class _VmsItemTagsModel(ItemTags):
    def to_supaiot_tags(self):
        supaiot_tags = {
            "CT": self.text or self.image_name or "",
            "FC": _ColorEnum.get_code_by_rgba(str(self.font_color)),
            "SH": self.screen_in_mode,
            "TI": self.duration,
            "FO": _FontEnum.get_code_by_font(str(self.font)),
        }
        ret = self.model_dump(exclude_none=True)
        ret.update({k: v for k, v in supaiot_tags.items() if v is not None})
        return ret


class _VmsPlayTagsModel(PlayTags):
    def to_supaiot_tags(self):
        supaiot_tags = {f"ZCT{i + 1}": "" for i in range(5)}
        for window in self.windows:
            for i, item in enumerate(window.items):
                j = i + 1
                content = item.text or item.image_name or ""  # 物联智控无法显示转义字符
                item_tags = {
                    f"FO{j}": _FontEnum.get_code_by_font(str(item.font)),
                    f"FC{j}": _ColorEnum.get_code_by_rgba(str(item.font_color)),
                    f"ZCT{j}": content,
                    f"TI{j}": item.duration,
                    f"SH{j}": item.screen_in_mode,
                }
                supaiot_tags.update({k: v for k, v in item_tags.items() if v is not None})

        ret = self.model_dump(exclude_none=True)
        ret.update(supaiot_tags)
        return ret


class _VmsBrightnessTagsModel(BrightnessTags):
    def to_supaiot_tags(self):
        supaiot_tags = {"TGFK": self.brightness, "LDMS": self.mode}
        ret = self.model_dump(exclude_none=True)
        ret.update({k: v for k, v in supaiot_tags.items() if v is not None})
        return ret


def convert(tags: BaseTags):
    """将SDK点位转为物联智控点位"""
    match tags:
        case ItemTags():
            return _VmsItemTagsModel(**tags.model_dump()).to_supaiot_tags()
        case PlayTags():
            return _VmsPlayTagsModel(**tags.model_dump()).to_supaiot_tags()
        case BrightnessTags():
            return _VmsBrightnessTagsModel(**tags.model_dump()).to_supaiot_tags()
        case _:
            # TODO: 添加操作成功的处理
            raise ValueError(f"{type(tags)} is not supported")


# ==============================================================================
# 控制点位
# ==============================================================================
class ControlVmsTagsModel(BaseModel):
    """情报板控制点位"""

    model_config = ConfigDict(populate_by_name=True)

    # 播放控制
    KFC1: Literal["1", "2", "3"] | None = Field(
        default=None,
        alias="font_color_of_item1",
        description="第一条目字体颜色，1是黄色，2是红色，3是绿色，下同",
    )
    KFO1: Literal["107", "115", "104", "102"] | None = Field(
        default=None,
        alias="font_of_item1",
        description="第一条目字体类型，107是楷体，115是宋体，104是黑体，102是仿宋，下同",
    )
    KSH1: Literal["0", "1", "2", "3", "4", "5"] | None = Field(
        default=None,
        alias="screen_in_mode_of_item1",
        description="第一条目显示方式，1是立即显示，2是上移，3是下移，4是左移，5是右移， 下同",
    )
    KTI1: str | None = Field(
        default=None,
        alias="duration_of_item1",
        min_length=1,
        max_length=4299,
        description="第一条目停留时间, 单位秒",
        examples=["5"],
    )
    KZCT1: str | None = Field(
        default=None,
        alias="media_of_item1",
        min_length=1,
        max_length=100000,
        description="第一条目显示内容",
    )
    KFC2: Literal["1", "2", "3"] | None = Field(
        default=None,
        alias="font_color_of_item2",
        description="第二条目字体颜色，1是黄色，2是红色，3是绿色，下同",
    )
    KFO2: Literal["107", "115", "104", "102"] | None = Field(
        default=None,
        alias="font_of_item2",
        description="第二条目字体类型，107是楷体，115是宋体，104是黑体，102是仿宋，下同",
    )
    KSH2: Literal["0", "1", "2", "3", "4", "5"] | None = Field(
        default=None,
        alias="screen_in_mode_of_item2",
        description="第二条目显示方式，1是立即显示，2是上移，3是下移，4是左移，5是右移， 下同",
    )
    KTI2: str | None = Field(
        default=None,
        alias="duration_of_item2",
        min_length=1,
        max_length=4299,
        description="第二条目停留时间, 单位秒",
        examples=["5"],
    )
    KZCT2: str | None = Field(
        default=None,
        alias="media_of_item2",
        min_length=1,
        max_length=100000,
        description="第二条目显示内容",
    )

    KFC3: Literal["1", "2", "3"] | None = Field(
        default=None,
        alias="font_color_of_item3",
        description="第三条目字体颜色，1是黄色，2是红色，3是绿色，下同",
    )
    KFO3: Literal["107", "115", "104", "102"] | None = Field(
        default=None,
        alias="font_of_item3",
        description="第三条目字体类型，107是楷体，115是宋体，104是黑体，102是仿宋，下同",
    )
    KSH3: Literal["0", "1", "2", "3", "4", "5"] | None = Field(
        default=None,
        alias="screen_in_mode_of_item3",
        description="第三条目显示方式，1是立即显示，2是上移，3是下移，4是左移，5是右移， 下同",
    )
    KTI3: str | None = Field(
        default=None,
        alias="duration_of_item3",
        min_length=1,
        max_length=4299,
        description="第三条目停留时间, 单位秒",
        examples=["5"],
    )
    KZCT3: str | None = Field(
        default=None,
        alias="media_of_item3",
        min_length=1,
        max_length=100000,
        description="第三条目显示内容",
    )

    KFC4: Literal["1", "2", "3"] | None = Field(
        default=None,
        alias="font_color_of_item4",
        description="第四条目字体颜色，1是黄色，2是红色，3是绿色，下同",
    )
    KFO4: Literal["107", "115", "104", "102"] | None = Field(
        default=None,
        alias="font_of_item4",
        description="第四条目字体类型，107是楷体，115是宋体，104是黑体，102是仿宋，下同",
    )
    KSH4: Literal["0", "1", "2", "3", "4", "5"] | None = Field(
        default=None,
        alias="screen_in_mode_of_item4",
        description="第四条目显示方式，1是立即显示，2是上移，3是下移，4是左移，5是右移， 下同",
    )
    KTI4: str | None = Field(
        default=None,
        alias="duration_of_item4",
        min_length=1,
        max_length=4299,
        description="第四条目停留时间, 单位秒",
        examples=["5"],
    )
    KZCT4: str | None = Field(
        default=None,
        alias="media_of_item4",
        min_length=1,
        max_length=100000,
        description="第四条目显示内容",
    )

    KFC5: Literal["1", "2", "3"] | None = Field(
        default=None,
        alias="font_color_of_item5",
        description="第五条目字体颜色，1是黄色，2是红色，3是绿色，下同",
    )
    KFO5: Literal["107", "115", "104", "102"] | None = Field(
        default=None,
        alias="font_of_item5",
        description="第五条目字体类型，107是楷体，115是宋体，104是黑体，102是仿宋，下同",
    )
    KSH5: Literal["0", "1", "2", "3", "4", "5"] | None = Field(
        default=None,
        alias="screen_in_mode_of_item5",
        description="第五条目显示方式，1是立即显示，2是上移，3是下移，4是左移，5是右移， 下同",
    )
    KTI5: str | None = Field(
        default=None,
        alias="duration_of_item5",
        min_length=1,
        max_length=4299,
        description="第五条目停留时间, 单位秒",
        examples=["5"],
    )
    KZCT5: str | None = Field(
        default=None,
        alias="media_of_item5",
        min_length=1,
        max_length=100000,
        description="第五条目显示内容",
    )

    KFC6: Literal["1", "2", "3"] | None = Field(
        default=None,
        alias="font_color_of_item6",
        description="第六条目字体颜色，1是黄色，2是红色，3是绿色，下同",
    )
    KFO6: Literal["107", "115", "104", "102"] | None = Field(
        default=None,
        alias="font_of_item6",
        description="第六条目字体类型，107是楷体，115是宋体，104是黑体，102是仿宋，下同",
    )
    KSH6: Literal["0", "1", "2", "3", "4", "5"] | None = Field(
        default=None,
        alias="screen_in_mode_of_item6",
        description="第六条目显示方式，1是立即显示，2是上移，3是下移，4是左移，5是右移， 下同",
    )
    KTI6: str | None = Field(
        default=None,
        alias="duration_of_item6",
        min_length=1,
        max_length=4299,
        description="第六条目停留时间, 单位秒",
        examples=["5"],
    )
    KZCT6: str | None = Field(
        default=None,
        alias="media_of_item6",
        min_length=1,
        max_length=100000,
        description="第六条目显示内容",
    )

    KFC7: Literal["1", "2", "3"] | None = Field(
        default=None,
        alias="font_color_of_item7",
        description="第七条目字体颜色，1是黄色，2是红色，3是绿色，下同",
    )
    KFO7: Literal["107", "115", "104", "102"] | None = Field(
        default=None,
        alias="font_of_item7",
        description="第七条目字体类型，107是楷体，115是宋体，104是黑体，102是仿宋，下同",
    )
    KSH7: Literal["0", "1", "2", "3", "4", "5"] | None = Field(
        default=None,
        alias="screen_in_mode_of_item7",
        description="第七条目显示方式，1是立即显示，2是上移，3是下移，4是左移，5是右移， 下同",
    )
    KTI7: str | None = Field(
        default=None,
        alias="duration_of_item7",
        min_length=1,
        max_length=4299,
        description="第七条目停留时间, 单位秒",
        examples=["5"],
    )
    KZCT7: str | None = Field(
        default=None,
        alias="media_of_item7",
        min_length=1,
        max_length=100000,
        description="第七条目显示内容",
    )

    KFC8: Literal["1", "2", "3"] | None = Field(
        default=None,
        alias="font_color_of_item8",
        description="第八条目字体颜色，1是黄色，2是红色，3是绿色，下同",
    )
    KFO8: Literal["107", "115", "104", "102"] | None = Field(
        default=None,
        alias="font_of_item8",
        description="第八条目字体类型，107是楷体，115是宋体，104是黑体，102是仿宋，下同",
    )
    KSH8: Literal["0", "1", "2", "3", "4", "5"] | None = Field(
        default=None,
        alias="screen_in_mode_of_item8",
        description="第八条目显示方式，1是立即显示，2是上移，3是下移，4是左移，5是右移， 下同",
    )
    KTI8: str | None = Field(
        default=None,
        alias="duration_of_item8",
        min_length=1,
        max_length=4299,
        description="第八条目停留时间, 单位秒",
        examples=["5"],
    )
    KZCT8: str | None = Field(
        default=None,
        alias="media_of_item8",
        min_length=1,
        max_length=100000,
        description="第八条目显示内容",
    )

    KFC9: Literal["1", "2", "3"] | None = Field(
        default=None,
        alias="font_color_of_item9",
        description="第九条目字体颜色，1是黄色，2是红色，3是绿色，下同",
    )
    KFO9: Literal["107", "115", "104", "102"] | None = Field(
        default=None,
        alias="font_of_item9",
        description="第九条目字体类型，107是楷体，115是宋体，104是黑体，102是仿宋，下同",
    )
    KSH9: Literal["0", "1", "2", "3", "4", "5"] | None = Field(
        default=None,
        alias="screen_in_mode_of_item9",
        description="第九条目显示方式，1是立即显示，2是上移，3是下移，4是左移，5是右移， 下同",
    )
    KTI9: str | None = Field(
        default=None,
        alias="duration_of_item9",
        min_length=1,
        max_length=4299,
        description="第九条目停留时间, 单位秒",
        examples=["5"],
    )
    KZCT9: str | None = Field(
        default=None,
        alias="media_of_item9",
        min_length=1,
        max_length=100000,
        description="第九条目显示内容",
    )

    KFC10: Literal["1", "2", "3"] | None = Field(
        default=None,
        alias="font_color_of_item10",
        description="第十条目字体颜色，1是黄色，2是红色，3是绿色，下同",
    )
    KFO10: Literal["107", "115", "104", "102"] | None = Field(
        default=None,
        alias="font_of_item10",
        description="第十条目字体类型，107是楷体，115是宋体，104是黑体，102是仿宋，下同",
    )
    KSH10: Literal["0", "1", "2", "3", "4", "5"] | None = Field(
        default=None,
        alias="screen_in_mode_of_item10",
        description="第十条目显示方式，1是立即显示，2是上移，3是下移，4是左移，5是右移， 下同",
    )
    KTI10: str | None = Field(
        default=None,
        alias="duration_of_item10",
        min_length=1,
        max_length=4299,
        description="第十条目停留时间, 单位秒",
        examples=["5"],
    )
    KZCT10: str | None = Field(
        default=None,
        alias="media_of_item10",
        min_length=1,
        max_length=100000,
        description="第十条目显示内容",
    )
    # 亮度控制
    TGKZ: str | None = Field(default=None, alias="brightness", description="调光控制，用于情报板, 范围0-100")
    # 以限速标发布
    KZCT: str | None = Field(
        default=None,
        alias="speed_limit",
        description="限速标发布",
    )


class ControlCslsTagsModel(BaseModel):
    """限速标控制点位"""

    KZCT: str | None = Field(default=None, description="限速值, 用于限速标")
