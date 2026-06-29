"""Transport 传输层测试。"""

import pytest

from highway_sdk.core.exceptions import (
    ConnectionLostError,
    ConnectionTimeoutError,
)
from highway_sdk.core.transport import Transport


class TestTransport:
    """Transport 类测试。"""

    @pytest.mark.asyncio
    async def test_connect_success(self, mock_tcp_server):
        """测试成功连接。"""
        host, port = mock_tcp_server
        transport = Transport(host, port, timeout=1.0)

        await transport.connect()
        assert transport.is_connected
        await transport.disconnect()

    @pytest.mark.asyncio
    async def test_connect_timeout(self):
        """测试连接超时。"""
        # 使用不存在的地址
        transport = Transport("192.0.2.1", 9999, timeout=0.1)

        with pytest.raises(ConnectionTimeoutError):
            await transport.connect()

    @pytest.mark.asyncio
    async def test_disconnect(self, mock_tcp_server):
        """测试断开连接。"""
        host, port = mock_tcp_server
        transport = Transport(host, port, timeout=1.0)

        await transport.connect()
        assert transport.is_connected

        await transport.disconnect()
        assert not transport.is_connected

    @pytest.mark.asyncio
    async def test_send_receive(self, mock_tcp_server):
        """测试数据收发。"""
        host, port = mock_tcp_server
        transport = Transport(host, port, timeout=1.0)

        await transport.connect()

        # 发送数据
        test_data = b"hello"
        await transport.send(test_data)

        # 接收回显数据
        response = await transport.receive()
        assert response == test_data

        await transport.disconnect()

    @pytest.mark.asyncio
    async def test_request_response(self, mock_tcp_server):
        """测试请求-响应模式。"""
        host, port = mock_tcp_server
        transport = Transport(host, port, timeout=1.0)

        await transport.connect()

        # 发送并等待响应
        test_data = b"test request"
        response = await transport.request(test_data, timeout=1.0)
        assert response == test_data

        await transport.disconnect()

    @pytest.mark.asyncio
    async def test_send_without_connection(self):
        """测试未连接时发送数据。"""
        transport = Transport("127.0.0.1", 9999, timeout=1.0)

        with pytest.raises(ConnectionLostError):
            await transport.send(b"test")

    @pytest.mark.asyncio
    async def test_context_manager(self, mock_tcp_server):
        """测试上下文管理器。"""
        host, port = mock_tcp_server

        async with Transport(host, port, timeout=1.0) as transport:
            assert transport.is_connected
            await transport.send(b"test")

        # 退出上下文后应该断开
        assert not transport.is_connected

    @pytest.mark.asyncio
    async def test_auto_reconnect_config(self):
        """测试自动重连配置。"""
        transport = Transport(
            "127.0.0.1",
            9999,
            auto_reconnect=True,
            reconnect_interval=0.5,
            max_reconnect_attempts=3,
        )

        assert transport.auto_reconnect is True
        assert transport.reconnect_interval == 0.5
        assert transport.max_reconnect_attempts == 3
