"""CMS 文字布局工具模块。

提供厂商无关的文字自动布局工具，根据显示区域尺寸自动计算：
- 适配字号（二分查找最大字号使文字完整显示）
- 自动换行（逐字符遍历，超宽换行）
- 居中坐标 (x, y)

该工具不依赖任何厂商协议，调用方负责将结果填入 ``CmsPlayItem``。

Example:
    >>> from highway_sdk.vendors.cms import TextLayout
    >>> layout = TextLayout("前方施工减速慢行", w=96, h=96, size_range=[16, 24, 32, 48, 64])
    >>> result = layout.build()
    >>> result.size
    24
    >>> result.text
    '前方施工\\n减速慢行'
    >>> result.x, result.y
    (0, 12)
"""

from pydantic import BaseModel, Field


class TextLayoutResult(BaseModel):
    """文字布局结果。

    Attributes:
        text: 已换行的文本（用 ``\\n`` 分隔），调用方填入 ``CmsPlayItem.text``。
        lines: 换行后的行列表。
        size: 适配后的字号，调用方填入 ``CmsPlayItem.font_size``。
        x: 居中 X 坐标（像素），调用方填入 ``CmsPlayItem.x``。
        y: 居中 Y 坐标（像素），调用方填入 ``CmsPlayItem.y``。
        text_width: 文本占用宽度（像素）。
        text_height: 文本占用高度（像素）。
    """

    text: str = Field(..., description="已换行的文本（用 \\n 分隔）")
    lines: list[str] = Field(..., description="换行后的行列表")
    size: int = Field(..., description="适配后的字号")
    x: int = Field(..., ge=0, description="居中 X 坐标（像素）")
    y: int = Field(..., ge=0, description="居中 Y 坐标（像素）")
    text_width: int = Field(..., ge=0, description="文本占用宽度（像素）")
    text_height: int = Field(..., ge=0, description="文本占用高度（像素）")


class TextLayout:
    """文字自动布局工具（厂商无关）。

    根据显示区域尺寸和文本内容，自动计算合适的字号、换行和居中坐标，
    确保文字能够完整显示在指定区域内并上下左右居中。

    字符宽度计算规则：
        - ASCII 字符（半角）：字号 / 2
        - 非 ASCII 字符（如中文全角）：字号

    算法步骤：
        1. 二分查找最大字号使文字完整显示在 w×h 区域
        2. 逐字符遍历，超宽时自动换行
        3. 计算居中坐标 ``x = (w - text_w) // 2, y = (h - text_h) // 2``

    Example:
        >>> layout = TextLayout("一二三四五六七八九十", w=96, h=96, max_size=64, min_size=8)
        >>> result = layout.build()
        >>> result.size
        24
        >>> result.text
        '一二三四\\n五六七八\\n九十'
        >>> result.x, result.y
        (0, 12)
    """

    MIN_SIZE: int = 8

    def __init__(
        self,
        text: str,
        *,
        w: int,
        h: int,
        max_size: int | None = None,
        min_size: int = MIN_SIZE,
        size_range: list[int] | None = None,
        word_space: int = 0,
        line_space: int = 0,
    ) -> None:
        """初始化文字布局工具。

        Args:
            text: 要显示的文本内容。
            w: 显示区域宽度（像素）。
            h: 显示区域高度（像素）。
            max_size: 最大字号，默认为 ``min(w, h)``。
            min_size: 最小字号，默认为 8，下限为 ``MIN_SIZE``。
            size_range: 设备支持的字号列表（如 ``[16, 24, 32, 48, 64]``）。
                提供时，会从适配字号中选择最接近且不超出的列表值；
                若列表中所有值都大于适配字号，则取列表最小值。
            word_space: 字间距（像素），默认为 0。
            line_space: 行间距（像素），默认为 0。

        Raises:
            ValueError: 文本为空、区域尺寸非正、或最小字号大于最大字号。
        """
        if not text:
            raise ValueError("文本内容不能为空")
        if w <= 0 or h <= 0:
            raise ValueError("显示区域宽高必须大于 0")

        self.text = text
        self.w = w
        self.h = h
        self.max_size = min(max_size if max_size is not None else min(w, h), min(w, h))
        self.min_size = max(min_size, self.MIN_SIZE)
        self.size_range = sorted(size_range) if size_range else []
        self.word_space = word_space
        self.line_space = line_space

        if self.min_size > self.max_size:
            raise ValueError(
                f"最小字号（{self.min_size}）不能大于最大字号（{self.max_size}），"
                f"可能是显示区域过小或 min_size 设置过大"
            )

    def _calc_char_width(self, ch: str, size: int) -> int:
        """计算单个字符宽度。

        ASCII 字符（半角）为字号 / 2，非 ASCII 字符（如中文全角）为字号。
        """
        return int(size / 2) if ch.isascii() else size

    def _calc_text_area(self, size: int) -> tuple[int, int]:
        """计算指定字号下文本占用的区域大小。

        模拟逐字符换行，统计行数和最大行宽。

        Returns:
            (height, width) 文本占用的总高和总宽（像素）。
        """
        total_width = 0
        max_lines = 1
        line_width = 0

        for i, ch in enumerate(self.text):
            ch_w = self._calc_char_width(ch, size)
            if line_width == 0:
                line_width = ch_w
            else:
                line_width += self.word_space + ch_w

            if i != len(self.text) - 1:
                next_ch = self.text[i + 1]
                next_w = self._calc_char_width(next_ch, size)
                # 当前行加上下一字符将超出宽度，换行
                if line_width + self.word_space > self.w or line_width + self.word_space + next_w > self.w:
                    max_lines += 1
                    total_width = max(total_width, line_width)
                    line_width = 0
                    # 检查行数加 1 后是否超出高度
                    if max_lines * size + (max_lines - 1) * self.line_space > self.h:
                        break
            else:
                total_width = max(total_width, line_width)

        text_height = max_lines * size + (max_lines - 1) * self.line_space
        return int(text_height), int(total_width)

    def _build_adjusted_size(self) -> tuple[int, int, int]:
        """二分查找最大适配字号。

        Returns:
            (size, text_height, text_width) 适配字号及对应文本占用高宽。
        """
        size = self.min_size
        text_h, text_w = self._calc_text_area(size)

        left, right = self.min_size, self.max_size
        while left <= right:
            mid = (left + right) // 2
            h, w = self._calc_text_area(mid)
            if w <= self.w and h <= self.h:
                size = mid
                text_h, text_w = h, w
                left = mid + 1
            else:
                right = mid - 1

        # 若指定设备支持的字号列表，选最接近且不超出的值
        if self.size_range:
            candidates = [s for s in self.size_range if s <= size]
            if candidates:
                size = max(candidates)
            else:
                size = self.size_range[0]
            text_h, text_w = self._calc_text_area(size)

        return size, text_h, text_w

    def _build_lines(self, size: int) -> str:
        """根据字号处理文本换行，返回用 ``\\n`` 分隔的文本。"""
        ch_list: list[str] = []
        line_width = 0

        for i, ch in enumerate(self.text):
            ch_list.append(ch)
            ch_w = self._calc_char_width(ch, size)
            if line_width == 0:
                line_width = ch_w
            else:
                line_width += self.word_space + ch_w

            if i != len(self.text) - 1:
                next_ch = self.text[i + 1]
                next_w = self._calc_char_width(next_ch, size)
                if line_width + self.word_space > self.w or line_width + self.word_space + next_w > self.w:
                    ch_list.append("\n")
                    line_width = 0

        return "".join(ch_list)

    def build(self) -> TextLayoutResult:
        """构建并返回文字布局结果。

        依次执行：
            1. 二分查找适配字号
            2. 逐字符换行
            3. 计算居中坐标

        Returns:
            TextLayoutResult: 布局结果，包含 text/lines/size/x/y 等字段。
        """
        size, text_h, text_w = self._build_adjusted_size()
        text = self._build_lines(size)
        lines = text.split("\n")
        x = max((self.w - text_w) // 2, 0)
        y = max((self.h - text_h) // 2, 0)
        return TextLayoutResult(
            text=text,
            lines=lines,
            size=size,
            x=round(x),
            y=round(y),
            text_width=text_w,
            text_height=text_h,
        )
