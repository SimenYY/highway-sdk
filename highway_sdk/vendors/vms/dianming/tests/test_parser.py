from highway_sdk.vendors.vms.dianming.parser import Parser
from highway_sdk.vendors.vms.dianming.spec import Frame


class TestParser:
    """测试解析器"""

    def test_parse_get_brightness_and_mode(self):
        """测试解析获取亮度和控制亮度模式响应"""
        frame = Frame.from_bytes(bytes.fromhex("02 30 31 30 30 32 32 46 46 46 46 46 46 30 31 36 65 03"))

        tags = Parser.parse(frame)
        expect_tags = {
            "mode": 1,
            "brightness": 3,
        }
        assert tags.model_dump(mode="json") == expect_tags
