#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:FileName: test_SanSiClient.py
:Project:
:Brand:
:Version:
:Description: 
:Author: He YinYu
:Link:
:Time: 2024/8/23 14:47
"""
from unittest.mock import patch, call

import pytest
from highway_sdk.vms.SanSi.v4_21_0.internet.sanSiClient import SanSiClient
from highway_sdk.vms.SanSi.v4_21_0.media import PlayBuilder, ItemBuilder, WinBuilder, MediaBuilder
from highway_sdk.vms.SanSi.v4_21_0.internet.utils.constants import SanSiReturnCode


class TestSanSiClient:

    @pytest.fixture
    def sansi_client(self):
        return SanSiClient()

    @pytest.fixture
    def play_list(self):
        pass

    @patch('socket.socket')
    def test_set_play_list_success(self, mock_socket, sansi_client, play_list):
        sansi_client.sock = mock_socket
        sansi_client.sock.recv.side_effect = [
            b'\x02\x30\x31\x30\xC5\x52\x03'
        ]

        result = sansi_client.set_play_list()
        assert result == SanSiReturnCode.SUCCESS

        # 测试发送报文的正确性
        excepted_send_call = [
            call(b'\x020010play.lst+\x00\x00\x00\x00\xda\xaf\x03')
        ]
        mock_socket.send.assert_has_calls(excepted_send_call)

    @patch('socket.socket')
    def test_get_now_play_content_success(self, mock_socket, sansi_client):
        sansi_client.sock = mock_socket
        sansi_client.sock.recv.side_effect = [
            b'\x02\x30\x31\x30\x30\x30\x30\x30\x35\x30\x30\x30\x31\x30\x30\x30\x30\x30\x5C\x66\x73\x32\x34\x32\x34'
            b'\x5C\x63\x30\x30\x30\x32\x35\x35\x30\x30\x30\x30\x30\x30\xCB\xED\xB5\xC0\xC2\xB7\xB6\xCE\x5C\x6E\xBD'
            b'\xF7\xC9\xF7\xBC\xDD\xCA\xBB\xE7\x4F\x03'
        ]
        result = sansi_client.get_now_play_content()
        excepted_result = r'\fs2424\c000255000000隧道路段\n谨慎驾驶'

        assert result == excepted_result

        # 测试发送报文的正确性
        excepted_send_call = [
            call(b'\x02\x30\x30\x39\x37\x10\xF5\x03')
        ]
        mock_socket.send.assert_has_calls(excepted_send_call)


if __name__ == '__main__':
    pytest.main([__file__])