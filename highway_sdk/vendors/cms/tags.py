"""CMS 标签数据模型模块。

定义了 CMS（可变情报板）通信中使用的统一标签数据模型。
"""

from datetime import datetime

from pydantic import BaseModel, Field


class CmsPlayItem(BaseModel):
    """cms 播放项 — 统一子结构。

    ``play_item`` 和 ``play_list`` 中每一项共用此结构。
    """

    index: int | None = Field(
        default=None,
        description="在 play_list 中的序号（从 0 开始）。仅 get_play_item 返回的 play_item 填充此字段；play_list 中各元素的 index 为 None",
        examples=[0, 1, 2],
    )
    text: str | None = Field(
        default=None,
        description="显示的文本内容。图片播放项时为 None",
        examples=["前方施工，减速慢行"],
    )
    font: str | None = Field(
        default=None,
        description="字体名称",
        examples=["黑体", "楷体", "宋体", "仿宋"],
    )
    font_color: str | None = Field(
        default=None,
        description="字体颜色",
        examples=["#FF0000", "#000000"],
    )
    font_size: int | None = Field(
        default=None,
        description="字体大小",
        examples=[24, 32, 48],
    )
    image_name: str | None = Field(
        default=None,
        description="图片文件名称。文本播放项时为 None",
        examples=["warning_sign.jpg"],
    )
    duration: int | None = Field(
        default=None,
        description="该条内容的停留时间，单位秒",
        examples=[10, 30, 60],
    )


class CmsTags(BaseModel):
    """cms 设备统一 Tags。

    三个数据采集 API 统一返回此结构，各 API 只填充相关字段，其余为 None。
    """

    orig_play_item: str | None = Field(
        default=None,
        description="当前播放项，保留厂家原始协议格式字符串。get_play_item 时填充",
    )
    orig_play_list: str | None = Field(
        default=None,
        description="当前播放列表，保留厂家原始协议格式字符串。get_play_list 时填充",
    )
    play_item: CmsPlayItem | None = Field(
        default=None,
        description="当前播放项（结构化），含 index 标识是 play_list 的第几项。get_play_item 时填充",
    )
    play_list: list[CmsPlayItem] = Field(
        default_factory=list,
        description="当前播放列表（结构化），get_play_list 时填充",
    )
    brightness: int | None = Field(
        default=None,
        ge=0,
        le=100,
        description="当前亮度百分比 0-100。get_brightness 时填充，品牌不支持时为 None",
        examples=[80],
    )
    brightness_mode: str | None = Field(
        default=None,
        description="亮度控制模式。get_brightness 时填充，品牌不支持时为 None",
        examples=["auto", "manual"],
    )
    timestamp: datetime = Field(
        ...,
        description="数据采集时间",
    )
