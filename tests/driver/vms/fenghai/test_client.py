import threading
import socketserver
import pytest
import pytest_asyncio
from tests.driver.conftest import TCPFendhaiHandler
from highway_sdk.core.protocols import TCPReconnectingConnector


class TestVmsFenghaiClient:
    @pytest.fixture(scope="class")
    def mock_tcp_server(self):
        HOST, PORT = "127.0.0.1", 8888
        with socketserver.ThreadingTCPServer((HOST, PORT), TCPFendhaiHandler) as server:
            server_thread = threading.Thread(target=server.serve_forever)
            server_thread.daemon = True
            server_thread.start()
            yield server

    @pytest_asyncio.fixture(scope="class")
    async def client(self):
        connector = await