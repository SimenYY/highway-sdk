from dataclasses import dataclass, asdict, field
import json


@dataclass
class BaseTags:
    def to_dict(self):
        return asdict(self)

    def __str__(self) -> str:
        return json.dumps(self.to_dict(), indent=4, ensure_ascii=False)


@dataclass
class ItemTags(BaseTags):
    """当前显示点位"""

    index: str | None = None
    meida: str | None = None  # 原始字符串
    content: str | None = None
    font: str | None = None  # 字体
    font_size: str | None = None  # 字体大小
    font_color: str | None = None  # 字体颜色
    background_color: str | None = None  # 背景颜色
    word_space: int | None = None  # 字间距
    text: str | None = None  # 文本字符串
    image_name: str | None = None  # 图片名称
    image_type: str | None = None  # 图片类型
    bmp: str | None = None
    gif: str | None = None
    jpg: str | None = None
    png: str | None = None
    mpg: str | None = None
    duration: int | None = None  # 停留时间，单位秒
    screen_in: str | None = None  # 入屏方式
    screen_out: str | None = None  # 出屏方式
    play_speed: int | None = None  # 播放速度
    

@dataclass
class WindowTags(BaseTags):
    """当前窗口点位

    Args:
        BaseTags (_type_): _description_
    """

    items: list[ItemTags] = field(default_factory=list)
    w: int | None = None  # 窗口宽度
    h: int | None = None  # 窗口高度
    x: int | None = None
    y: int | None = None

@dataclass
class PlayTags(BaseTags):
    """
    当前播放点位列表
    """

    windows: list[WindowTags] = field(default_factory=list)


@dataclass
class BrightnessTags(BaseTags):
    """
    当前亮度点位
    """

    brightness: int | None = None
