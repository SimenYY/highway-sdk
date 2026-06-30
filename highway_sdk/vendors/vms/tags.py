"""VMS 标签数据模型模块。

定义了 VMS（可变情报板）通信中使用的各种标签数据模型。
"""

from enum import IntEnum

from pydantic import Field

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
    duration: int | None = Field(default=None, description="停留时间，单位秒")
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
