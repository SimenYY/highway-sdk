#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from unittest.mock import MagicMock, patch
from vms.nova.v3_11_5.internet.novaClient import NovaClient
from vms.nova.v3_11_5.internet.utils.constants import NovaOkRsp


@pytest.fixture
def nova_traffic():
    return NovaClient(ip="127.0.0.1")


@patch('socket.socket')
def test_send_play_list_success(mock_socket, nova_traffic):
    mock_sock = MagicMock()
    mock_socket.return_value.__enter__.return_value = mock_sock
    mock_sock.recv.side_effect = [
        NovaOkRsp.FILE_NAME_OK_RSP,
        NovaOkRsp.FILE_CONTENT_OK_RSP,
        NovaOkRsp.PLAY_LIST_OK_RSP,
    ]

    result = nova_traffic.send_play_list(content="test content", play_id=1)
    assert result is True


@patch('socket.socket')
def test_send_play_list_connection_refused(mock_socket, nova_traffic):
    mock_socket.return_value.__enter__.side_effect = ConnectionRefusedError("Connection refused")

    result = nova_traffic.send_play_list(content="test content", play_id=1)
    assert result is False


@patch('socket.socket')
def test_send_play_list_timeout(mock_socket, nova_traffic):
    mock_sock = MagicMock()
    mock_socket.return_value.__enter__.return_value = mock_sock
    mock_sock.recv.side_effect = TimeoutError("Timeout error")

    result = nova_traffic.send_play_list(content="test content", play_id=1)
    assert result is False


@patch('socket.socket')
def test_send_play_list_nova_file_name_error(mock_socket, nova_traffic):
    mock_sock = MagicMock()
    mock_socket.return_value.__enter__.return_value = mock_sock
    mock_sock.recv.side_effect = [
        b'\x00\x00\x00\x00\x00\x00',  # Invalid response
    ]

    result = nova_traffic.send_play_list(content="test content", play_id=1)
    assert result is False


@patch('socket.socket')
def test_send_play_list_nova_file_content_error(mock_socket, nova_traffic):
    mock_sock = MagicMock()
    mock_socket.return_value.__enter__.return_value = mock_sock
    mock_sock.recv.side_effect = [
        NovaOkRsp.FILE_NAME_OK_RSP,
        b'\x00\x00\x00\x00\x00\x00',  # Invalid response
    ]

    result = nova_traffic.send_play_list(content="test content", play_id=1)
    assert result is False


@patch('socket.socket')
def test_send_play_list_nova_play_list_error(mock_socket, nova_traffic):
    mock_sock = MagicMock()
    mock_socket.return_value.__enter__.return_value = mock_sock
    mock_sock.recv.side_effect = [
        NovaOkRsp.FILE_NAME_OK_RSP,
        NovaOkRsp.FILE_CONTENT_OK_RSP,
        b'\x00\x00\x00\x00\x00\x00',  # Invalid response
    ]

    result = nova_traffic.send_play_list(content="test content", play_id=1)
    assert result is False
