"""VMS 标签数据模型模块。

定义了 VMS（可变情报板）通信中使用的各种标签数据模型，
包括厂商原生 Tags 和 cms 统一 Tags（CmsTags / CmsPlayItem）。
"""

from datetime import datetime
from enum import IntEnum

from pydantic import BaseModel, Field

from highway_sdk.core.tags import BaseTags


class BrightnessMode(IntEnum):
    """亮度模式。"""

    AUTO = 0  # 自动模式
    MANUAL = 1  # 手动模式


class OperationTags(BaseTags):
    """操作结果标签。"""

    is_ok: bool | None = Field(default=None, description="操作是否成功")


class MediaTags(BaseTags):
    """媒体标签。"""

    media: str | None = Field(default=None, description="原始媒体")
    font: str | None = Field(default=None, description="字体")
    font_size: int | None = Field(default=None, description="字体大小")
    font_color: str | None = Field(default=None, description="字体颜色")
    background_color: str | None = Field(default=None, description="背景颜色")
    word_space: int | None = Field(default=None, description="字间距")
    text: str | None = Field(default=None, description="文本字符串")
    image_name: str | None = Field(default=None, description="图片名称")
    image_type: str | None = Field(default=None, description="图片类型")
    bmp: str | None = Field(default=None, description="BMP格式图片")
    gif: str | None = Field(default=None, description="GIF格式图片")
    jpg: str | None = Field(default=None, description="JPG格式图片")
    png: str | None = Field(default=None, description="PNG格式图片")
    mpg: str | None = Field(default=None, description="MPG格式视频")


class ItemTags(BaseTags):
    """播放项标签。"""

    index: str | None = Field(default=None, description="播放项索引")
    media: str | None = Field(default=None, description="原始媒体")
    media_list: list[MediaTags] = Field(default_factory=list, description="媒体列表")
    duration: int | None = Field(default=None, description="停留时间，单位十分之一秒")
    screen_in_mode: int | None = Field(default=None, description="入屏方式")
    screen_out_mode: int | None = Field(default=None, description="出屏方式")
    play_speed: int | None = Field(default=None, description="播放速度")
    play_effect: int | None = Field(default=None, description="播放效果")


class WindowTags(BaseTags):
    """窗口标签。"""

    items: list[ItemTags] = Field(default_factory=list, description="窗口中的项目列表")
    w: int | None = Field(default=None, description="窗口宽度")
    h: int | None = Field(default=None, description="窗口高度")
    x: int | None = Field(default=None, description="窗口横坐标")
    y: int | None = Field(default=None, description="窗口纵坐标")


class PlayTags(BaseTags):
    """播放标签。"""

    windows: list[WindowTags] = Field(default_factory=list, description="播放窗口列表")


class BrightnessTags(BaseTags):
    """亮度标签。"""

    brightness: int | None = Field(default=None, ge=0, le=100, description="亮度百分比")
    mode: BrightnessMode | None = Field(default=None, description="调节模式")


class ScreenTags(BaseTags):
    """屏幕尺寸标签。"""

    width: int | None = Field(default=None, description="屏幕宽度")
    height: int | None = Field(default=None, description="屏幕高度")


# ---------------------------------------------------------------------------
# cms 统一 Tags（Sprint 1）
# ---------------------------------------------------------------------------


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
