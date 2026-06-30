"""厂商注册表模块。

提供厂商元数据定义、注册和发现机制，支持物联网平台动态加载设备协议。
"""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from highway_sdk.core.device import BaseDevice


@dataclass(frozen=True, slots=True)
class VendorMetadata:
    """厂商元数据。

    Attributes:
        name: 厂商标识符（唯一键），如 "dianming"。
        display_name: 厂商显示名称，如 "电明"。
        device_type: 设备类型，如 "vms", "vd"。
        description: 厂商描述。
        device_class: 设备类（延迟导入时使用字符串）。
        codec_class: 编解码器类（延迟导入时使用字符串）。
        version: 协议版本。
        tags: 额外标签信息。
    """

    name: str
    display_name: str
    device_type: str
    description: str
    device_class: type["BaseDevice"] | str
    codec_class: type | str
    version: str = "1.0.0"
    tags: dict[str, Any] = field(default_factory=dict)


class VendorRegistry:
    """厂商注册表。

    管理所有已注册的厂商实现，提供注册、查询和工厂功能。
    """

    def __init__(self):
        self._vendors: dict[str, VendorMetadata] = {}

    def register(self, metadata: VendorMetadata) -> None:
        """注册厂商。

        Args:
            metadata: 厂商元数据。

        Raises:
            ValueError: 厂商已存在。
        """
        if metadata.name in self._vendors:
            raise ValueError(f"Vendor '{metadata.name}' already registered")
        self._vendors[metadata.name] = metadata

    def get(self, name: str) -> VendorMetadata:
        """获取厂商元数据。

        Args:
            name: 厂商标识符。

        Returns:
            VendorMetadata: 厂商元数据。

        Raises:
            KeyError: 厂商不存在。
        """
        if name not in self._vendors:
            raise KeyError(f"Vendor '{name}' not found")
        return self._vendors[name]

    def list(self) -> list[VendorMetadata]:
        """列出所有已注册厂商。

        Returns:
            list[VendorMetadata]: 厂商元数据列表。
        """
        return list(self._vendors.values())

    def create_device(self, vendor: str, host: str, port: int, **kwargs: Any) -> "BaseDevice":
        """创建设备实例。

        Args:
            vendor: 厂商标识符。
            host: 设备地址。
            port: 设备端口。
            **kwargs: 传递给设备连接的参数。

        Returns:
            BaseDevice: 设备实例（未连接状态）。

        Raises:
            KeyError: 厂商不存在。
        """
        metadata = self.get(vendor)
        device_cls = metadata.device_class

        # 如果是字符串，需要延迟导入
        if isinstance(device_cls, str):
            module_path, class_name = device_cls.rsplit(".", 1)
            import importlib

            module = importlib.import_module(module_path)
            device_cls = getattr(module, class_name)

        # 创建设备实例（未连接）
        from highway_sdk.core.transport import Transport

        transport = Transport(host, port, **kwargs)
        return device_cls(transport)

    async def connect_device(self, vendor: str, host: str, port: int, **kwargs: Any) -> "BaseDevice":
        """创建并连接设备。

        Args:
            vendor: 厂商标识符。
            host: 设备地址。
            port: 设备端口。
            **kwargs: 传递给设备连接的参数。

        Returns:
            BaseDevice: 已连接的设备实例。
        """
        metadata = self.get(vendor)
        device_cls = metadata.device_class

        # 如果是字符串，需要延迟导入
        if isinstance(device_cls, str):
            module_path, class_name = device_cls.rsplit(".", 1)
            import importlib

            module = importlib.import_module(module_path)
            device_cls = getattr(module, class_name)

        return await device_cls.connect(host, port, **kwargs)


# 全局注册表实例
registry = VendorRegistry()


def register_vendor(metadata: VendorMetadata) -> None:
    """注册厂商到全局注册表。

    Args:
        metadata: 厂商元数据。
    """
    registry.register(metadata)


def get_vendor(name: str) -> VendorMetadata:
    """获取厂商元数据。

    Args:
        name: 厂商标识符。

    Returns:
        VendorMetadata: 厂商元数据。
    """
    return registry.get(name)


def list_vendors() -> list[VendorMetadata]:
    """列出所有已注册厂商。

    Returns:
        list[VendorMetadata]: 厂商元数据列表。
    """
    return registry.list()


def create_device(vendor: str, host: str, port: int, **kwargs: Any) -> "BaseDevice":
    """创建设备实例（未连接）。

    Args:
        vendor: 厂商标识符。
        host: 设备地址。
        port: 设备端口。
        **kwargs: 传递给 Transport 的参数。

    Returns:
        BaseDevice: 设备实例。
    """
    return registry.create_device(vendor, host, port, **kwargs)


async def connect_device(vendor: str, host: str, port: int, **kwargs: Any) -> "BaseDevice":
    """创建并连接设备。

    Args:
        vendor: 厂商标识符。
        host: 设备地址。
        port: 设备端口。
        **kwargs: 传递给设备连接的参数。

    Returns:
        BaseDevice: 已连接的设备实例。
    """
    return await registry.connect_device(vendor, host, port, **kwargs)
