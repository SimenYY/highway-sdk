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
    x: int | None = Field(
        default=None,
        ge=0,
        description="渲染坐标 X（像素），None 时厂商使用默认值 0。配合 TextLayout 工具实现居中显示",
        examples=[0, 48],
    )
    y: int | None = Field(
        default=None,
        ge=0,
        description="渲染坐标 Y（像素），None 时厂商使用默认值 0。配合 TextLayout 工具实现居中显示",
        examples=[0, 32],
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

    def flatten(self) -> dict[str, int | float | str]:
        """扁平化输出为 k-v 字典，排除所有 None 值。

        - 标量字段（orig_play_item / orig_play_list / brightness / brightness_mode）直接输出
        - play_item（单个播放项）字段名直接作为 key
        - play_list（播放列表）字段名加序号后缀，如 text_0、font_1
        - timestamp 转为 ISO 8601 字符串

        Returns:
            dict[str, int | float | str]: 扁平化后的键值对，值仅为 int/float/str
        """
        result: dict[str, int | float | str] = {}

        # 标量字段
        for name in ("orig_play_item", "orig_play_list", "brightness", "brightness_mode"):
            value = getattr(self, name)
            if value is not None:
                result[name] = value

        # play_item（单个播放项）—— 字段名直接作为 key
        if self.play_item is not None:
            for k, v in self.play_item.model_dump(exclude_none=True).items():
                result[k] = v if isinstance(v, (int, float, str)) else str(v)

        # play_list（播放列表）—— 字段名加序号后缀，如 text_0、font_0
        for i, item in enumerate(self.play_list):
            result[f"index_{i}"] = i
            for k, v in item.model_dump(exclude_none=True).items():
                if k == "index":
                    continue  # 列表序号已作为 index_N 填充
                result[f"{k}_{i}"] = v if isinstance(v, (int, float, str)) else str(v)

        # timestamp 转为 ISO 字符串
        result["timestamp"] = self.timestamp.isoformat()

        return result
