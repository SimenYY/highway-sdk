"""VMS标签数据模型模块。

该模块定义了VMS（可变情报板）通信中使用的各种标签数据模型，
包括操作标签、播放项标签、窗口标签、播放标签和亮度标签。
"""

from highway_sdk.core.base import BaseTags
from pydantic import Field


class OperationTags(BaseTags):
    """操作结果标签。

    用于表示设备操作的结果状态。

    Attributes:
        is_ok: 操作是否成功。
    """

    is_ok: bool | None = Field(default=None, description="操作是否成功")


class ItemTags(BaseTags):
    """播放项标签。

    用于表示单个播放项的详细信息，包括文本、图片、视频等媒体内容，
    以及播放相关的参数如持续时间、入屏方式等。

    Attributes:
        index: 播放项索引。
        meida: 原始媒体数据。
        font: 字体类型。
        font_size: 字体大小。
        font_color: 字体颜色。
        background_color: 背景颜色。
        word_space: 字间距。
        text: 文本字符串（不带转义符，例如换行符）。
        image_name: 图片名称（不包括扩展名）。
        image_type: 图片类型。
        bmp: BMP格式图片。
        gif: GIF格式图片。
        jpg: JPG格式图片。
        png: PNG格式图片。
        mpg: MPG格式视频。
        duration: 停留时间，单位秒。
        screen_in_mode: 入屏方式。
        screen_out_mode: 出屏方式。
        play_speed: 播放速度。
        play_effect: 播放效果。
    """

    index: str | None = Field(default=None, description="播放项索引")
    meida: str | None = Field(default=None, description="原始媒体")
    font: str | None = Field(default=None, description="字体")
    font_size: int | None = Field(default=None, description="字体大小")
    font_color: str | None = Field(default=None, description="字体颜色")
    background_color: str | None = Field(default=None, description="背景颜色")
    word_space: int | None = Field(default=None, description="字间距")
    text: str | None = Field(
        default=None, description="文本字符串（不带转义符，例如换行符）"
    )
    image_name: str | None = Field(default=None, description="图片名称(不包括扩展名)")
    image_type: str | None = Field(default=None, description="图片类型")
    bmp: str | None = Field(default=None, description="BMP格式图片")
    gif: str | None = Field(default=None, description="GIF格式图片")
    jpg: str | None = Field(default=None, description="JPG格式图片")
    png: str | None = Field(default=None, description="PNG格式图片")
    mpg: str | None = Field(default=None, description="MPG格式视频")

    duration: int | None = Field(default=None, description="停留时间，单位秒")
    screen_in_mode: int | None = Field(default=None, description="入屏方式")
    screen_out_mode: int | None = Field(default=None, description="出屏方式")
    play_speed: int | None = Field(default=None, description="播放速度")
    play_effect: int | None = Field(default=None, description="播放效果")


class WindowTags(BaseTags):
    """窗口标签。

    用于表示显示窗口的配置信息，包括窗口中的播放项列表和窗口的位置尺寸。

    Attributes:
        items: 窗口中的项目列表。
        w: 窗口宽度。
        h: 窗口高度。
        x: 窗口横坐标。
        y: 窗口纵坐标。
    """

    items: list[ItemTags] = Field(default_factory=list, description="窗口中的项目列表")
    w: int | None = Field(default=None, description="窗口宽度")
    h: int | None = Field(default=None, description="窗口高度")
    x: int | None = Field(default=None, description="窗口横坐标")
    y: int | None = Field(default=None, description="窗口纵坐标")


class PlayTags(BaseTags):
    """播放标签。

    用于表示播放列表的完整信息，包含所有播放窗口。

    Attributes:
        windows: 播放窗口列表。
    """

    windows: list[WindowTags] = Field(default_factory=list, description="播放窗口列表")


class BrightnessTags(BaseTags):
    """亮度标签。

    用于表示设备的亮度设置信息。

    Attributes:
        brightness: 亮度百分比，范围1-100。
        mode: 调节模式。
    """

    brightness: int | None = Field(default=None, ge=1, le=100, description="亮度百分比")
    mode: int | None = Field(default=None, description="调节模式")

