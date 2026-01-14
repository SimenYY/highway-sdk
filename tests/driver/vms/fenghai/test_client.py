import socketserver
import threading

import pytest
import pytest_asyncio

from highway_sdk.core.protocols import TCPReconnectingConnector
from tests.driver.conftest import TCPFendhaiHandler


class TestVmsFenghaiClient:
    @pytest.fixture(scope="class")
    def mock_tcp_server(self):
        host, port = "127.0.0.1", 8888
        with socketserver.ThreadingTCPServer((host, port), TCPFendhaiHandler) as server:
            server_thread = threading.Thread(target=server.serve_forever)
            server_thread.daemon = True
            server_thread.start()
            yield server

    @pytest_asyncio.fixture(scope="class")
    async def client(self):
        connector = TCPReconnectingConnector(
            host="127.0.0.1", port=8888, reconnect_interval=1, max_reconnect_attempts=3
        )
        yield connector
