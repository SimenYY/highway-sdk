"""pytest 配置和共享 fixtures。"""

import asyncio
from collections.abc import AsyncGenerator

import pytest_asyncio


@pytest_asyncio.fixture
async def mock_tcp_server() -> AsyncGenerator[tuple[str, int], None]:
    """模拟 TCP 服务器，用于测试。"""
    host = "127.0.0.1"
    port = 9999

    async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """处理客户端连接。"""
        try:
            while True:
                data = await reader.read(1024)
                if not data:
                    break
                # 回显数据（简单模拟）
                writer.write(data)
                await writer.drain()
        except Exception:
            pass
        finally:
            writer.close()
            await writer.wait_closed()

    server = await asyncio.start_server(handle_client, host, port)
    async with server:
        yield host, port
