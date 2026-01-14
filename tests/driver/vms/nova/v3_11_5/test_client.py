import textwrap

import pytest

from highway_sdk.vendors.vms.nova.client import VmsNovaClient
from highway_sdk.vendors.vms.nova.spec import NovaMsg
from tests.mock.mock_server import VmsNovaMock_v3_11_5


class TestVmsNovaClient:
    """VMS Nova Client 集成测试"""

    @pytest.fixture(scope="class")
    def mock_server(self):
        server = VmsNovaMock_v3_11_5(host="127.0.0.1", port=8888)
        server.start()

        yield server

        server.stop()

    @pytest.fixture(scope="class")
    def client(self, mock_server: VmsNovaMock_v3_11_5):
        client = VmsNovaClient.connect(host=mock_server.host, port=mock_server.port)

        yield client

        client.disconnect()

    def test_client_connect(self, client: VmsNovaClient):
        assert client.is_connected

    def test_send_file_name(self, client: VmsNovaClient):
        client.send_file_name("play001.lst")

    def test_send_file_content(self, client: VmsNovaClient):
        content = (
            textwrap.dedent("""
                [all]
                items=1
                [item1]
                param=100,1,1,1,0,5,1
                txtext1=0,0,0,280,3,4848,0,0,0,1,0,1,8,0,2,100,1,马尔康欢迎您。,1,1,0,5,5,5""")
            .lstrip()
            .replace("\n", "\r\n")
        )
        client.send_file_content(content=content)

    def test_play_playlist(self, client: VmsNovaClient):
        client.play_playlist(1)

    def test_get_play(self, client: VmsNovaClient):
        data = client.get_play()

        expected = (
            textwrap.dedent("""
                [all]
                items=1
                [item1]
                param=100,1,1,1,0,5,1,0,1
                txt1=10,0,3,1616,1,8,0,车牌：冀A318AA大货车,192,320,0
                txtparam1=0,0""")
            .lstrip()
            .encode(NovaMsg.encoding)
        )
        assert data[1:] == expected

    def test_get_item(self, client: VmsNovaClient):
        data = client.get_item()

        expected = (
            textwrap.dedent("""
                [item1]
                param=100,1,1,1,0,5,1,0,1
                txt1=10,0,3,1616,1,8,0,车牌：冀A318AA大货车,192,320,0
                txtparam1=0,0""")
            .lstrip()
            .encode(NovaMsg.encoding)
        )
        assert data[3:] == expected

    def test_get_now_brightness(self, client: VmsNovaClient):
        data = client.get_now_brightness()

        expected = b"\x02\xff"

        assert data == expected

    def test_get_screen_size(self, client: VmsNovaClient):
        data = client.get_screen_size()

        expected = b"\xa0\x02\xc0\x01"

        assert data == expected
