import pytest
import time
from unittest.mock import MagicMock, patch, call
from highway_sdk.vms.nova.v3_11_5.internet.novaClient import NovaClient
from highway_sdk.vms.nova.v3_11_5.internet.utils.constants import get_success_rsp, NovaWhat, NovaReturnCode


class TestNovaClient:
    @pytest.fixture
    def nova_client(self):
        return NovaClient("127.0.0.1", 5000)

    @patch('socket.socket')
    def test_set_play_list_success(self, mock_socket, nova_client):
        nova_client._sock = mock_socket
        nova_client._sock.recv.side_effect = [
            get_success_rsp(NovaWhat.FILE_NAME_RSP),
            get_success_rsp(NovaWhat.FILE_CONTENT_RSP),
            get_success_rsp(NovaWhat.PLAY_LIST_RSP)
        ]
        result = nova_client.set_play_list("")
        assert result == NovaReturnCode.SUCCESS

        # 测试发送报文正确性
        expected_send_calls = [
            call(b'\xAA\xFF\xFF\x11\xFF\xFF\x70\x6C\x61\x79\x30\x30\x31\x2E\x6C\x73\x74\xCC\x5A\x9B'),
            call(b'\xaa\xff\xff\x13\x01\xcc\x7d\xee'),
            call(b'\xAA\xFF\xFF\x1B\x01\xCC\xBF\x28'),
        ]
        mock_socket.send.assert_has_calls(expected_send_calls, any_order=False)

    @patch('socket.socket')
    def test_set_play_list_host_response_timeout(self, mock_socket, nova_client):
        nova_client._sock = mock_socket
        nova_client._sock.recv.side_effect = [
            TimeoutError
        ]
        result = nova_client.set_play_list("")
        assert result == NovaReturnCode.HOST_RESPONSE_TIMEOUT

        nova_client._sock.recv.side_effect = [
            get_success_rsp(NovaWhat.FILE_NAME_RSP),
            TimeoutError,
        ]
        result = nova_client.set_play_list("")
        assert result == NovaReturnCode.HOST_RESPONSE_TIMEOUT

        nova_client._sock.recv.side_effect = [
            get_success_rsp(NovaWhat.FILE_NAME_RSP),
            get_success_rsp(NovaWhat.FILE_CONTENT_RSP),
            TimeoutError,
        ]
        result = nova_client.set_play_list("")
        assert result == NovaReturnCode.HOST_RESPONSE_TIMEOUT

    @patch('socket.socket')
    def test_set_play_list_host_response_error(self, mock_socket, nova_client):
        nova_client._sock = mock_socket
        nova_client._sock.recv.side_effect = [
            b'\xAA\xFF\xFF\x12\x01\xCC\xA2\xB4',  # wrong crc
            get_success_rsp(NovaWhat.FILE_CONTENT_RSP),
            get_success_rsp(NovaWhat.PLAY_LIST_RSP)
        ]

        result = nova_client.set_play_list("")
        assert result == NovaReturnCode.PROTOCOL_PARSER_ERROR

        nova_client._sock.recv.side_effect = [
            b'\xAA\xFF\xFF\x1C\x01\xCC\xBA\xA4',  # wrong flag
            get_success_rsp(NovaWhat.FILE_CONTENT_RSP),
            get_success_rsp(NovaWhat.PLAY_LIST_RSP)
        ]

        result = nova_client.set_play_list("")
        assert result == NovaReturnCode.PROTOCOL_PARSER_ERROR

        nova_client._sock.recv.side_effect = [
            b'\xAA\xFF\xFF\xCC\xA1\xB4',  # wrong length
            get_success_rsp(NovaWhat.FILE_CONTENT_RSP),
            get_success_rsp(NovaWhat.PLAY_LIST_RSP)
        ]

        result = nova_client.set_play_list("")
        assert result == NovaReturnCode.PROTOCOL_PARSER_ERROR

    @patch('socket.socket')
    def test_set_play_list_socket_error(self, mock_socket, nova_client):
        nova_client._sock = None

        result = nova_client.set_play_list("")
        assert result == NovaReturnCode.SOCKET_ERROR

    @patch('socket.socket')
    def test_get_device_size_none(self, mock_socket, nova_client):
        nova_client._sock = None
        result = nova_client.get_device_size()
        assert result is None

        nova_client._sock = mock_socket
        nova_client._sock.recv.side_effect = [
            TimeoutError
        ]
        result = nova_client.get_device_size()
        assert result is None

    @patch('socket.socket')
    @pytest.mark.skip('等待收集成功响应的报文')
    def test_get_device_size_success(self, mock_socket, nova_client):
        nova_client._sock = mock_socket
        nova_client._sock.recv.side_effect = [
            # todo 收集成功响应的报文
        ]
        result = nova_client.get_device_size()
        assert type(result) == tuple

    @patch('socket.socket')
    def get_now_play_content_none(self, mock_socket, nova_client):
        nova_client._sock = None
        result = nova_client.get_now_play_content()
        assert result is None

        nova_client._sock = mock_socket
        nova_client._sock.recv.side_effect = [
            TimeoutError
        ]
        result = nova_client.get_now_play_content()
        assert result is None

    @patch('socket.socket')
    @pytest.mark.skip('等待收集成功响应的报文')
    def test_get_now_play_content_success(self, mock_socket, nova_client):
        nova_client._sock = mock_socket

    @patch('socket.socket')
    def get_now_play_all_content_none(self, mock_socket, nova_client):
        nova_client._sock = None
        result = nova_client.get_now_play_all_content()
        assert result is None

        nova_client._sock = mock_socket
        nova_client._sock.recv.side_effect = [
            TimeoutError
        ]
        result = nova_client.get_now_play_all_content()
        assert result is None

    @patch('socket.socket')
    @pytest.mark.skip('等待收集成功响应的报文')
    def test_get_now_play_all_content_success(self, mock_socket, nova_client):
        nova_client._sock = mock_socket
        nova_client._sock.recv.side_effect = [
            # todo
        ]
        result = nova_client.get_now_play_all_content()


if __name__ == '__main__':
    pytest.main([__file__])
