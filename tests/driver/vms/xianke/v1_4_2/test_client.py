import textwrap
import pytest
from tests.mock.mock_server import VmsXiankeMock_v1_4_2
from highway_sdk.vendors.vms.xianke.client import VmsXianKeClient


class TestXiankeClient:
    
    @pytest.fixture(scope="class")
    def mock_server(self):
        server = VmsXiankeMock_v1_4_2(host="127.0.0.1", port=8888)
        server.start()
        
        yield server
        
        server.stop()
        
    
    @pytest.fixture(scope="class")
    def client(self, mock_server: VmsXiankeMock_v1_4_2):
        client = VmsXianKeClient.connect(mock_server.host, mock_server.port)

        yield client
        
        client.disconnect()
        
    
    def test_upload_file(self, client: VmsXianKeClient):
        content = (
            textwrap.dedent(r"""
            [LIST]
            ItemCount=002
            Item00=2,1,0,1,1,\C000000\Fs32\T255000000000\B000000000000\U深圳显科科技有限公司 
            Item01=2,1,0,1,1,\C000000\Fs32\T000255000000\B000000000000\U深圳显科科技有限公司
        """)
            .lstrip()
            .replace("\n", "\r\n")
            .replace(" ", "")
        )
        client.upload_file(content, "list\\000.xkl")
    
    
    def test_play_playlist(self, client: VmsXianKeClient):
        client.play_list()

