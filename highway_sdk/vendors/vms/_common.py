"""VMS通用工具模块。

该模块提供了VMS（可变情报板）文本显示相关的通用工具类，
包括文本模型和文本建造器，用于自动调整文本大小、换行和位置。
"""

from typing import Literal

from pydantic import BaseModel, Field


class _VmsTextModel(BaseModel):
    """VMS文本数据模型。

    用于表示情报板上显示的文本及其相关属性。

    Attributes:
        text: 文本内容。
        lf: 换行符。
        word_space: 字间距。
        line_space: 行间距。
        font_color: 字体颜色。
        size: 字号。
        lines: 文本行列表。
        xy: 文本起始坐标。
        text_area: 文本占用区域尺寸（高度，宽度）。
    """

    text: str = Field(..., description="文本")
    lf: str = Field(default="\n", description="换行符")
    word_space: int = Field(default=0, description="字间距")
    line_space: int = Field(default=0, description="行间距")
    font_color: Literal["red", "yellow", "green", "black"] = Field(default="red", description="字体颜色")
    size: int = Field(default=16, description="字号")
    lines: list[str] = Field(default=[], description="文本行列表的形式")
    xy: tuple[int, int] = Field(default=(0, 0), description="文本起始坐标")
    text_area: tuple[int, int] | None = Field(default=None, description="文本占用区域尺寸, h, w")


class VmsTextBuilder:
    """VMS文本建造器。

    该类用于根据给定的显示区域大小和文本内容，自动计算合适的字体大小、
    文本换行和显示位置，确保文本能够完整显示在指定的区域内。

    Example:
        >>> dtb = VmsTextBuilder(text='一二三四五六七八九十', h=96, w=96, max_size=275, min_size=6)
        >>> print(dtb.build().size)
        24
        >>> print(dtb.build().text)
        一二三四
        五六七八
        九十
        >>> print(dtb.build().xy)
        (0, 10)
        >>> print(dtb.build().lines)
        ['一二三四', '五六七八', '九十']
    """

    MIN_SIZE: int = 8

    def __init__(
        self,
        text: str,
        *,
        h: int,
        w: int,
        max_size: int,
        min_size: int,
        font_color: Literal["red", "yellow", "green", "black"] = "red",
        background_color: Literal["red", "yellow", "green", "black"] = "black",
        line_space: int = 0,
        word_space: int = 0,
        size_range: list | None = None,
        lf: str = "\n",
    ):
        """初始化VMS文本建造器。

        Args:
            text: 要显示的文本内容。
            h: 显示区域高度。
            w: 显示区域宽度。
            max_size: 最大字号。
            min_size: 最小字号。
            font_color: 字体颜色。
            background_color: 背景颜色。
            line_space: 行间距。
            word_space: 字间距。
            size_range: 设备支持的字号列表。
            lf: 换行符。
        """
        self.text = text
        self.h = h
        self.w = w
        self.max_size = min(max_size, min(h, w))
        self.min_size = max(min_size, self.MIN_SIZE)
        self.background_color = background_color
        if size_range is None:
            self.size_list = []
        else:
            self.size_list = sorted(list(size_range))
        self.lf = lf

        self.vms_text_model = _VmsTextModel(text=text)
        self.vms_text_model.lf = self.lf
        self.vms_text_model.line_space = line_space
        self.vms_text_model.word_space = word_space
        self.vms_text_model.font_color = font_color

    def _calc_text_len(self, size: int, text: str) -> int:
        """计算文本占阵列大小总长度。

        Args:
            size: 字体大小。
            text: 文本内容。

        Returns:
            int: 文本总长度。
        """
        length = 0
        for ch in text:
            if ch.isascii():
                length += size / 2 + self.vms_text_model.word_space
            else:
                length += size + self.vms_text_model.word_space
        return int(length) - self.vms_text_model.word_space

    @staticmethod
    def max_less_than(compared: int, num_list: list[int]) -> int | None:
        """在整数列表中找出小于或等于给定值的最大值。

        Args:
            compared: 比较值。
            num_list: 整数列表。

        Returns:
            int | None: 小于或等于compared的最大值，如果没有则返回None。
        """
        return max((num for num in num_list if num <= compared), default=None)

    def build(self) -> _VmsTextModel:
        """构建并返回显示文本模型。

        该方法会依次执行以下步骤：
        1. 调整字体大小
        2. 处理文本换行
        3. 计算显示位置

        Returns:
            _VmsTextModel: 构建完成的文本模型。
        """
        self._build_adjusted_size()
        self._build_lines()
        self._build_xy()

        return self.vms_text_model

    def _build_adjusted_size(self) -> None:
        """获取合适的字体大小。

        使用二分查找算法在给定的字号范围内找到最大的合适字号，
        使得文本能够完整显示在指定的区域内。
        """

        def calc_text_area(size):
            """计算指定字号下文本占用的区域大小。"""
            total_width = 0
            total_height = 0
            max_lines = 1
            clw = 0

            letter_s = self.vms_text_model.word_space
            line_s = self.vms_text_model.line_space
            text = self.text
            width = self.w
            height = self.h

            for i, ch in enumerate(text):
                ch_w = size / 2 if ch.isascii() else size

                if ch_w == 0:
                    ch_w += ch_w
                else:
                    clw += letter_s + ch_w

                if i != (len(text) - 1):
                    next_ch_w = size / 2 if text[i + 1].isascii() else size
                    if clw + letter_s > width or clw + letter_s + next_ch_w > width:
                        max_lines += 1
                        total_height = max_lines * size + (max_lines - 1) * line_s

                        if total_height > height:
                            break

                        total_width = max(clw, total_width)
                        clw = 0
                else:
                    total_width = max(clw, total_width)
                    total_height = max_lines * size + (max_lines - 1) * line_s

            return int(total_height), int(total_width)

        left, right = self.min_size, self.max_size
        self.vms_text_model.size = self.min_size
        self.vms_text_model.text_area = (self.h, self.w)
        while left <= right:
            mid = (left + right) // 2

            text_height, text_width = calc_text_area(mid)

            if text_width <= self.w and text_height <= self.h:
                self.vms_text_model.text_area = (text_height, text_width)
                self.vms_text_model.size = mid
                left = mid + 1
            else:
                right = mid - 1

        if self.size_list:
            suited_size = self.max_less_than(self.vms_text_model.size, self.size_list)
            if suited_size is None:
                self.vms_text_model.size = self.size_list[0]
            else:
                self.vms_text_model.size = suited_size
            self.vms_text_model.text_area = calc_text_area(self.vms_text_model.size)

    def _build_lines(self) -> None:
        """获取换行调整的文本。

        根据计算出的字体大小和显示区域宽度，自动处理文本换行。
        """
        clw = 0
        letter_s = self.vms_text_model.word_space
        ch_list = []
        for i, ch in enumerate(self.text):
            ch_list.append(ch)

            ch_w = self.vms_text_model.size / 2 if ch.isascii() else self.vms_text_model.size
            if clw == 0:
                clw += ch_w
            else:
                clw += letter_s + ch_w

            if i != (len(self.text) - 1):
                next_ch_w = self.vms_text_model.size / 2 if self.text[i + 1].isascii() else self.vms_text_model.size
                if (clw + letter_s > self.w) or (clw + letter_s + next_ch_w > self.w):
                    ch_list.append(self.vms_text_model.lf)
                    clw = 0

        self.vms_text_model.text = "".join(ch_list)
        self.vms_text_model.lines = self.vms_text_model.text.split(self.lf)

    def _build_xy(self) -> None:
        """计算文本显示坐标点，默认左上角。

        根据文本实际占用的区域大小和显示区域大小，
        计算文本的起始坐标，使文本居中显示。
        """
        text_h, text_w = self.h, self.w
        if self.vms_text_model.text_area:
            text_h, text_w = self.vms_text_model.text_area
        x = max((self.w - text_w) // 2, 0)
        y = max((self.h - text_h) // 2, 0)

        self.vms_text_model.xy = (round(x), round(y))
