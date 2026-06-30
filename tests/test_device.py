"""Device 设备基类测试。"""

import pytest

from highway_sdk.core.codec import BaseCodec
from highway_sdk.core.device import BaseDevice
from highway_sdk.core.frame import BaseFrame
from highway_sdk.core.tags import BaseTags
from highway_sdk.core.transport import Transport


class MockFrame(BaseFrame):
    """测试用帧。"""

    @classmethod
    def from_bytes(cls, message: bytes) -> "MockFrame":
        return cls(what=message[:4], data=message[4:])

    def __bytes__(self) -> bytes:
        return self.what + self.data


class MockCodec(BaseCodec):
    """模拟编解码器。"""

    @classmethod
    def decode_test(cls, data: bytes) -> BaseTags:
        return BaseTags()


MockCodec._decoders[b"test"] = MockCodec.decode_test.__func__


class MockDevice(BaseDevice):
    """模拟设备。"""

    codec = MockCodec

    async def test_operation(self) -> BaseTags:
        """测试操作。"""
        frame = MockFrame(what=b"test", data=b"test_data")
        response = await self.request(frame)
        return self.codec.decode(MockFrame(what=b"test", data=response))


class TestBaseDevice:
    """BaseDevice 类测试。"""

    @pytest.mark.asyncio
    async def test_device_creation(self, mock_tcp_server):
        """测试设备创建。"""
        host, port = mock_tcp_server
        transport = Transport(host, port, timeout=1.0)
        await transport.connect()

        device = MockDevice(transport)
        assert device.transport is transport
        assert device.codec is MockCodec

        await transport.disconnect()

    @pytest.mark.asyncio
    async def test_device_connect_classmethod(self, mock_tcp_server):
        """测试类方法连接。"""
        host, port = mock_tcp_server

        device = await MockDevice.connect(host, port, timeout=1.0)
        assert isinstance(device, MockDevice)
        assert device.transport.is_connected

        await device.disconnect()

    @pytest.mark.asyncio
    async def test_device_context_manager(self, mock_tcp_server):
        """测试上下文管理器。"""
        host, port = mock_tcp_server

        async with await MockDevice.connect(host, port, timeout=1.0) as device:
            assert device.transport.is_connected

        # 退出后应该断开
        assert not device.transport.is_connected

    @pytest.mark.asyncio
    async def test_device_send(self, mock_tcp_server):
        """测试发送帧。"""
        host, port = mock_tcp_server

        async with await MockDevice.connect(host, port, timeout=1.0) as device:
            frame = MockFrame(what=b"test", data=b"hello")
            await device.send(frame)

    @pytest.mark.asyncio
    async def test_device_request(self, mock_tcp_server):
        """测试请求-响应。"""
        host, port = mock_tcp_server

        async with await MockDevice.connect(host, port, timeout=1.0) as device:
            frame = MockFrame(what=b"test", data=b"test_data")
            response = await device.request(frame, timeout=1.0)
            assert response == b"testtest_data"  # what + data 被回显

    @pytest.mark.asyncio
    async def test_device_operation(self, mock_tcp_server):
        """测试设备操作。"""
        host, port = mock_tcp_server

        async with await MockDevice.connect(host, port, timeout=1.0) as device:
            result = await device.test_operation()
            assert isinstance(result, BaseTags)

    @pytest.mark.asyncio
    async def test_custom_transport_factory(self, mock_tcp_server):
        """测试自定义传输层工厂。"""
        host, port = mock_tcp_server

        def custom_factory(h, p, **kwargs):
            return Transport(h, p, timeout=2.0, **kwargs)

        device = await MockDevice.connect(host, port, transport_factory=custom_factory)
        assert device.transport.timeout == 2.0

        await device.disconnect()
