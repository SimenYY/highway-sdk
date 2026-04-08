from highway_sdk.vendors.vms.dianming.factory import FrameFactory


class TestFrameFactory:
    """测试工厂类"""

    def test_get_brightness_and_mode(self):
        """测试获取亮度和控制亮度模式"""
        frame = FrameFactory.get_brightness_and_mode()
        assert bytes(frame) == bytes.fromhex("02 30 30 30 31 32 31 B8 9B 03")

    def test_set_brightness_or_mode(self):
        """测试设置亮度或控制亮度模式"""
        frame = FrameFactory.set_brightness_or_mode()
        assert bytes(frame) == bytes.fromhex("02 30 30 30 31 32 33 46 46 46 46 46 46 0E 04 03")
