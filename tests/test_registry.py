"""测试厂商注册表模块。"""

import pytest

from highway_sdk import (
    VendorMetadata,
    create_device,
    get_vendor,
    list_vendors,
)
from highway_sdk.vendors.registry import VendorRegistry


class TestVendorMetadata:
    """测试 VendorMetadata 数据类。"""

    def test_metadata_creation(self):
        """测试元数据创建。"""
        metadata = VendorMetadata(
            name="test_vendor",
            display_name="测试厂商",
            device_type="cms",
            description="测试描述",
            device_class="test_module.TestDevice",
            codec_class="test_module.TestCodec",
        )
        assert metadata.name == "test_vendor"
        assert metadata.display_name == "测试厂商"
        assert metadata.device_type == "cms"
        assert metadata.version == "1.0.0"

    def test_metadata_frozen(self):
        """测试元数据不可变。"""
        metadata = VendorMetadata(
            name="test",
            display_name="测试",
            device_type="cms",
            description="测试",
            device_class="test.TestDevice",
            codec_class="test.TestCodec",
        )
        with pytest.raises(AttributeError):
            metadata.name = "new_name"


class TestVendorRegistry:
    """测试 VendorRegistry 注册表。"""

    def test_register_and_get(self):
        """测试注册和获取厂商。"""
        registry = VendorRegistry()
        metadata = VendorMetadata(
            name="test",
            display_name="测试",
            device_type="cms",
            description="测试",
            device_class="test.TestDevice",
            codec_class="test.TestCodec",
        )
        registry.register(metadata)
        result = registry.get("test")
        assert result == metadata

    def test_register_duplicate(self):
        """测试重复注册抛出异常。"""
        registry = VendorRegistry()
        metadata = VendorMetadata(
            name="test",
            display_name="测试",
            device_type="cms",
            description="测试",
            device_class="test.TestDevice",
            codec_class="test.TestCodec",
        )
        registry.register(metadata)
        with pytest.raises(ValueError, match="already registered"):
            registry.register(metadata)

    def test_get_not_found(self):
        """测试获取不存在的厂商抛出异常。"""
        registry = VendorRegistry()
        with pytest.raises(KeyError, match="not found"):
            registry.get("nonexistent")

    def test_list_vendors(self):
        """测试列出所有厂商。"""
        registry = VendorRegistry()
        metadata1 = VendorMetadata(
            name="vendor1",
            display_name="厂商1",
            device_type="cms",
            description="描述1",
            device_class="test.TestDevice1",
            codec_class="test.TestCodec1",
        )
        metadata2 = VendorMetadata(
            name="vendor2",
            display_name="厂商2",
            device_type="cms",
            description="描述2",
            device_class="test.TestDevice2",
            codec_class="test.TestCodec2",
        )
        registry.register(metadata1)
        registry.register(metadata2)
        vendors = registry.list()
        assert len(vendors) == 2
        assert metadata1 in vendors
        assert metadata2 in vendors


class TestGlobalRegistry:
    """测试全局注册表功能。"""

    def test_list_vendors_returns_all(self):
        """测试 list_vendors 返回所有已注册厂商。"""
        vendors = list_vendors()
        assert len(vendors) >= 5  # 至少有5个内置厂商
        vendor_names = {v.name for v in vendors}
        assert "dianming" in vendor_names
        assert "fenghai" in vendor_names
        assert "nova" in vendor_names
        assert "sansi" in vendor_names
        assert "xianke" in vendor_names

    def test_get_vendor(self):
        """测试 get_vendor 获取特定厂商。"""
        vendor = get_vendor("dianming")
        assert vendor.name == "dianming"
        assert vendor.display_name == "电明"
        assert vendor.device_type == "cms"

    def test_create_device(self):
        """测试 create_device 创建设备实例（未连接）。"""
        device = create_device("dianming", "127.0.0.1", 9000)
        assert device is not None
        assert device.transport.host == "127.0.0.1"
        assert device.transport.port == 9000

    def test_create_device_invalid_vendor(self):
        """测试 create_device 使用无效厂商名抛出异常。"""
        with pytest.raises(KeyError, match="not found"):
            create_device("nonexistent", "127.0.0.1", 9000)
