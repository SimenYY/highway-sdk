"""TextLayout 文字布局工具单元测试。

测试用例来源：
- sdk-v2.x.x VmsTextBuilder docstring 示例（移植验证）
- 边界情况与 size_range 参数行为
"""

import pytest

from highway_sdk.vendors.cms import TextLayout, TextLayoutResult


class TestTextLayoutChinese:
    """中文文本布局测试（基于 VmsTextBuilder docstring 示例）。"""

    def test_ten_chars_96x96(self):
        """10个中文字符在 96×96 区域：字号24、3行、居中坐标 (0, 12)。

        sdk-v2.x.x VmsTextBuilder docstring 示例（原版 xy=(0,10) 有误，
        正确值为 (0, 12)：text_height=72, (96-72)//2=12）。
        """
        layout = TextLayout("一二三四五六七八九十", w=96, h=96, max_size=64, min_size=8)
        result = layout.build()

        assert result.size == 24
        assert result.text == "一二三四\n五六七八\n九十"
        assert result.lines == ["一二三四", "五六七八", "九十"]
        assert result.text_width == 96  # 4 * 24
        assert result.text_height == 72  # 3 * 24
        assert result.x == 0  # (96 - 96) // 2
        assert result.y == 12  # (96 - 72) // 2

    def test_short_text_no_wrap(self):
        """短文本2字，字号取最大，单行居中。"""
        layout = TextLayout("你好", w=96, h=96, max_size=48)
        result = layout.build()

        assert result.size == 48
        assert result.text == "你好"
        assert result.lines == ["你好"]
        assert result.text_width == 96  # 2 * 48
        assert result.text_height == 48  # 1 * 48
        assert result.x == 0  # (96 - 96) // 2
        assert result.y == 24  # (96 - 48) // 2

    def test_single_char(self):
        """单字符取最大字号，完全居中。"""
        layout = TextLayout("字", w=96, h=96, max_size=64)
        result = layout.build()

        assert result.size == 64
        assert result.text == "字"
        assert result.text_width == 64
        assert result.text_height == 64
        assert result.x == 16  # (96 - 64) // 2
        assert result.y == 16  # (96 - 64) // 2


class TestTextLayoutAscii:
    """ASCII 文本布局测试（字符宽度为字号 / 2）。"""

    def test_pure_ascii(self):
        """纯 ASCII 文本：5字符在字号32时宽度=5*16=80<=96。"""
        layout = TextLayout("Hello", w=96, h=96, max_size=32)
        result = layout.build()

        assert result.size == 32
        assert result.text == "Hello"
        assert result.text_width == 80  # 5 * (32 / 2)
        assert result.text_height == 32  # 1 * 32

    def test_mixed_chinese_ascii(self):
        """中英文混合：字号32时 '你好He' 一行(96)，'llo' 一行。"""
        layout = TextLayout("你好Hello", w=96, h=96, max_size=32)
        result = layout.build()

        assert result.size == 32
        assert result.text == "你好He\nllo"
        assert result.lines == ["你好He", "llo"]
        assert result.text_width == 96  # max(2*32 + 2*16, 3*16) = max(96, 48) = 96
        assert result.text_height == 64  # 2 * 32
        assert result.x == 0
        assert result.y == 16  # (96 - 64) // 2


class TestTextLayoutSizeRange:
    """size_range 参数测试（设备支持的字号列表）。"""

    def test_snap_to_smaller_in_range(self):
        """适配字号24，size_range=[16,32,48] 应选16（最接近且不超出）。"""
        layout = TextLayout("一二三四五六七八九十", w=96, h=96, max_size=64, size_range=[16, 32, 48])
        result = layout.build()

        assert result.size == 16

    def test_exact_match_in_range(self):
        """适配字号正好在 size_range 中。"""
        layout = TextLayout("你好", w=96, h=96, max_size=48, size_range=[16, 24, 32, 48])
        result = layout.build()

        assert result.size == 48

    def test_all_exceed_take_min(self):
        """适配字号小于 size_range 所有值，取列表最小值。"""
        # 超长文本使适配字号降到最小
        layout = TextLayout("一二三四五六七八九十" * 5, w=96, h=96, max_size=96, min_size=8, size_range=[16, 32, 48])
        result = layout.build()

        # 50个中文字符，即使字号16也无法完整显示，但 size_range 强制取最小16
        assert result.size == 16

    def test_no_size_range_free_size(self):
        """不提供 size_range 时，字号为二分查找的连续值。"""
        layout = TextLayout("你好", w=100, h=100, max_size=50)
        result = layout.build()

        # 2个中文字符，字号50时宽度=100<=100，合适
        assert result.size == 50


class TestTextLayoutValidation:
    """输入验证测试。"""

    def test_empty_text_raises(self):
        with pytest.raises(ValueError, match="文本内容不能为空"):
            TextLayout("", w=96, h=96)

    def test_zero_width_raises(self):
        with pytest.raises(ValueError, match="显示区域宽高必须大于 0"):
            TextLayout("你好", w=0, h=96)

    def test_zero_height_raises(self):
        with pytest.raises(ValueError, match="显示区域宽高必须大于 0"):
            TextLayout("你好", w=96, h=0)

    def test_negative_width_raises(self):
        with pytest.raises(ValueError, match="显示区域宽高必须大于 0"):
            TextLayout("你好", w=-10, h=96)

    def test_min_size_greater_than_max_size_raises(self):
        """显示区域过小导致 min_size > max_size 时报错。"""
        with pytest.raises(ValueError, match="最小字号"):
            TextLayout("你好", w=10, h=10, max_size=4, min_size=8)

    def test_min_size_clamped_to_min_size_constant(self):
        """min_size 低于 MIN_SIZE(8) 时被钳制为 8。"""
        layout = TextLayout("你好", w=96, h=96, min_size=4)
        assert layout.min_size == 8

    def test_max_size_clamped_to_min_dimension(self):
        """max_size 大于 min(w,h) 时被钳制为 min(w,h)。"""
        layout = TextLayout("你好", w=96, h=64, max_size=128)
        assert layout.max_size == 64

    def test_max_size_defaults_to_min_dimension(self):
        """不提供 max_size 时默认为 min(w, h)。"""
        layout = TextLayout("你好", w=96, h=64)
        assert layout.max_size == 64


class TestTextLayoutResult:
    """TextLayoutResult 数据结构测试。"""

    def test_result_is_text_layout_result(self):
        layout = TextLayout("你好", w=96, h=96, max_size=48)
        result = layout.build()
        assert isinstance(result, TextLayoutResult)

    def test_result_fields_populated(self):
        layout = TextLayout("你好", w=96, h=96, max_size=48)
        result = layout.build()

        assert result.text == "你好"
        assert result.lines == ["你好"]
        assert result.size == 48
        assert result.x == 0
        assert result.y == 24
        assert result.text_width == 96
        assert result.text_height == 48

    def test_result_lines_count_matches_text(self):
        """lines 数量与 text 中 \\n 分隔的行数一致。"""
        layout = TextLayout("一二三四五六七八九十", w=96, h=96, max_size=64, min_size=8)
        result = layout.build()

        assert len(result.lines) == result.text.count("\n") + 1


class TestTextLayoutEdgeCases:
    """边界情况测试。"""

    def test_text_fits_exactly(self):
        """文本恰好填满区域，不换行。"""
        # 4个中文字符，字号24，宽度=4*24=96，正好等于 w=96
        layout = TextLayout("一二三四", w=96, h=96, max_size=24)
        result = layout.build()

        assert result.size == 24
        assert result.text == "一二三四"
        assert result.lines == ["一二三四"]

    def test_word_space(self):
        """字间距影响换行。"""
        # 无字间距时2字符48*2=96刚好放下；加1字间距后48*2+1=97>96需换行
        layout = TextLayout("你好", w=96, h=96, max_size=48, word_space=1)
        result = layout.build()

        # 字号48+字间距1：'你'(48), '好'(48+1+48=97>96) 需换行
        # 但字号48时2行高度=2*48=96<=96，合适
        assert result.text == "你\n好"
        assert result.lines == ["你", "好"]

    def test_line_space(self):
        """行间距影响高度计算。"""
        # 2行字号48，无行间距高度=96<=96；行间距1高度=96+1=97>96不合适
        layout = TextLayout("你好", w=48, h=96, max_size=48, line_space=0)
        result = layout.build()

        # 字号48时'你'(48), '好'(48+48=96>48)需换行。2行*48=96<=96，合适
        assert result.text == "你\n好"
        assert result.text_height == 96

    def test_text_too_long_for_area(self):
        """文本过长无法完整显示时，使用最小字号并尽力换行。"""
        # 100个字符在 48×48 区域，即使最小字号8也放不下
        layout = TextLayout("字" * 100, w=48, h=48, max_size=48, min_size=8)
        result = layout.build()

        # 应使用最小字号8，不抛异常
        assert result.size == 8


class TestTextLayoutIntegration:
    """与 CmsPlayItem 集成测试。"""

    def test_layout_result_to_cms_play_item(self):
        """验证 TextLayout 结果可填入 CmsPlayItem。"""
        from highway_sdk.vendors.cms.tags import CmsPlayItem

        layout = TextLayout("前方施工减速慢行", w=96, h=96, size_range=[16, 24, 32, 48, 64])
        result = layout.build()

        item = CmsPlayItem(
            text=result.text,
            font_size=result.size,
            x=result.x,
            y=result.y,
            font_color="#FF0000",
            duration=10,
        )

        assert item.text == result.text
        assert item.font_size == result.size
        assert item.x == result.x
        assert item.y == result.y
        assert item.font_color == "#FF0000"
