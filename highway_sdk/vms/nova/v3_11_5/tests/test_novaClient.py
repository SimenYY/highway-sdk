import pytest
from unittest.mock import MagicMock, patch

from highway_sdk.vms.nova.v3_11_5.internet.novaClient import NovaClient
from highway_sdk.vms.nova.v3_11_5.internet.utils.constants import get_success_rsp, NovaWhat, NovaReturnCode


class TestNovaClient:
    @pytest.fixture
    def nova_client(self):
        return NovaClient("127.0.0.1", 5000)

    @patch('socket.socket')
    def test_set_play_list_success(self, mock_socket, nova_client):
        nova_client.sock = MagicMock()
        nova_client.sock.recv.side_effect = [
            get_success_rsp(NovaWhat.FILE_NAME_RSP),
            get_success_rsp(NovaWhat.FILE_CONTENT_RSP),
            get_success_rsp(NovaWhat.PLAY_LIST_RSP)
        ]
        result = nova_client.set_play_list("")
        assert result == NovaReturnCode.SUCCESS


if __name__ == '__main__':
    pytest.main([__file__])
