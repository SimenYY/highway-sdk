import re
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_serializer,
    IPvAnyAddress,
)
from typing import Any
from enum import IntEnum, StrEnum


class Prototype(BaseModel):
    """设备原型

    设计思路，这里主要的变化就是外部输入输出的字段变化，通过输入输出的别名进行控制
    """

    model_config = ConfigDict(
        extra="forbid",
        validate_by_alias=True,
        validate_by_name=True,
        use_enum_values=True,
    )


class NetworkNode(Prototype):
    """网络节点"""

    sn: str | None = Field(default=None, exclude=True, description="设备标识码")
    series: str | None = Field(default=None, exclude=True, description="设备产品序列号")
    host: IPvAnyAddress | None = Field(
        default=None, exclude=True, description="设备地址"
    )
    port: int | None = Field(default=None, exclude=True, description="设备端口")


class Csls(NetworkNode):
    """限速标"""

    realtime_content: str = Field(
        default="", serialization_alias="CT", description="实时内容"
    )

    play_content: str = Field(
        ...,
        validation_alias="KZCT",
        serialization_alias="ZCT",
        exclude=True,
        description="播放内容",
    )
    font_color: str | None = Field(
        default=None,
        validation_alias="KFC",
        serialization_alias="FC",
        description="字体颜色",
    )
    font: str | None = Field(
        default=None,
        validation_alias="KFO",
        serialization_alias="FO",
        description="字体",
    )
    font_size: int | None = Field(
        default=None,
        validation_alias="KFS",
        serialization_alias="FS",
        description="字体大小",
    )
    duration: int | None = Field(
        default=None,
        validation_alias="KTI",
        serialization_alias="TI",
        description="播放时长",
    )
    play_mode: int | None = Field(
        default=None,
        validation_alias="KSH",
        serialization_alias="SH",
        description="播放模式",
    )


class FontColor(StrEnum):
    YELLOW = "1"
    RED = "2"
    GREEN = "3"


class Font(StrEnum):
    KAI_TI = "107"
    SONG_TI = "115"
    HEI_TI = "104"
    FANG_SONG = "102"


class PlayMode(IntEnum):
    CLEAR = 0
    NORMAL = 1


class PlayItem(BaseModel):
    """情报板播放项"""

    font_color: FontColor = Field(
        ..., validation_alias="KFC", serialization_alias="FC", description="字体颜色"
    )
    font: Font = Field(
        ..., validation_alias="KFO", serialization_alias="FO", description="字体"
    )
    play_mode: PlayMode = Field(
        ..., validation_alias="KSH", serialization_alias="SH", description="显示模式"
    )
    duration: int = Field(
        ...,
        validation_alias="KTI",
        serialization_alias="TI",
        description="停留时间, 单位秒",
    )
    play_content: str = Field(
        ...,
        validation_alias="KZCT",
        serialization_alias="ZCT",
        description="显示内容, 返回文本or图片",
    )

    @field_validator("duration", mode="before")
    @classmethod
    def convert_str_to_int(cls, v: Any) -> int:
        if isinstance(v, str):
            if not v.isdigit():
                raise ValueError("duration must be a numeric string (e.g., '5')")
            return int(v)
        elif isinstance(v, int):
            return v
        else:
            raise ValueError("duration must be an integer or a numeric string")


class Vms(NetworkNode):
    """情报板"""

    height: int | None = Field(default=None, exclude=True, description="情报板高度")
    width: int | None = Field(default=None, exclude=True, description="情报板宽度")

    realtime_content: str = Field(
        default="", serialization_alias="CT", description="实时内容"
    )

    items: list[PlayItem] = Field(default_factory=list, description="播放项列表")

    @model_serializer(when_used="json-unless-none")
    def to_tags(self):
        flat = self.model_copy().model_dump(by_alias=True)  # 重新复制，避免递归调用
        items = flat.pop("items")
        # 扁平化 items 列表
        for i, item in enumerate(items, start=1):
            for key, value in item.items():
                flat[f"{key}{i}"] = value

        return flat

    @classmethod
    def create_from_tags(cls, tags: dict[str, Any]):
        """从扁平化点位构建"""
        items_dict: dict[int, dict[str, Any]] = {}

        index_pattern = re.compile(r"([A-Za-z]+)(\d+)")

        for k, v in tags.items():
            ret = index_pattern.search(k)
            if not ret:
                continue  # 匹配全部
            index = int(ret.group(2))
            field = ret.group(1)

            if index not in items_dict:
                items_dict[index] = {}

            items_dict[index][field] = v

        if not items_dict:
            return cls(items=[])

        sorted_items_dict = dict(sorted(items_dict.items()))
        items = []
        for _, v in sorted_items_dict.items():
            items.append(v)

        return cls(items=items)
