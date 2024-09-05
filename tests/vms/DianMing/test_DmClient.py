#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:FileName: test_DmClient.py
:Project:
:Brand:
:Version:
:Description: 
:Author: He YinYu
:Link:
:Time: 2024/8/21 10:26
"""
import pytest
from unittest.mock import patch, call

import socket
from highway_sdk.vms.DianMing.v2_3_0.internet.dmClient import DmClient
from highway_sdk.vms.DianMing.v2_3_0.internet.utils.constants import DmReturnCode
from highway_sdk.vms.DianMing.v2_3_0.internet.utils.crc import CrcUtils
from highway_sdk.vms.DianMing.v2_3_0.media.playBuilder import PlayBuilder
from highway_sdk.vms.DianMing.v2_3_0.media.itemBuilder import ItemBuilder
from highway_sdk.vms.DianMing.v2_3_0.media.mediaBuilder import MediaBuilder
from highway_sdk.vms.DianMing.v2_3_0.media.enums import FontEnum, ColorEnum

from loguru import logger


logger.remove()


class TestDmClient:

    def setup_method(self, method):
        media = MediaBuilder()
        media.x = 0
        media.y = 0
        media.font = FontEnum.SONG_TI.value
        media.text_size = 32
        media.text_color = ColorEnum.GREEN.value
        media.background_color = ColorEnum.BLACK.value
        media.text = 'Hello World'

        item = ItemBuilder()
        item.duration = 30
        item.add_media_builder(media)

        play = PlayBuilder()
        self.content = play.add_item_builder(item).build().create_msg()

    @pytest.fixture
    def dm_client(self):
        return DmClient(ip='127.0.0.1', port=5000)

    @patch('socket.socket')
    def test_set_play_list_success(self, mock_socket, dm_client):
        dm_client.sock = mock_socket
        dm_client.sock.recv.side_effect = [
            b'\x02\x30\x31\x30\x30\x37\x32\x31\x16\x16\x03'
        ]
        result = dm_client.set_play_list(content=self.content)
        assert result == DmReturnCode.SUCCESS

        # 测试发送报文正确性
        excepted_send_call = [
            call(b'\x02\x30\x30\x30\x31\x37\x31\x2b\x30\x30\x30\x30\x30\x30\x30\x30\x70\x6c\x61\x79\x30\x30\x2e\x6c\x73'
                 b'\x74\x5b\x50\x4c\x41\x59\x4c\x49\x53\x54\x5d\x0d\x0a\x49\x54\x45\x4d\x5f\x4e\x4f\x3d\x30\x30\x31\x0d'
                 b'\x0a\x49\x54\x45\x4d\x30\x30\x30\x3d\x33\x30\x2c\x30\x2c\x30\x2c\x30\x2c\x30\x2c\x5c\x43\x30\x30\x30'
                 b'\x30\x30\x30\x5c\x46\x73\x33\x32\x33\x32\x5c\x54\x30\x30\x30\x32\x35\x35\x30\x30\x30\x30\x30\x30\x5c'
                 b'\x4b\x30\x30\x30\x30\x30\x30\x30\x30\x30\x30\x30\x30\x5c\x57\x48\x65\x6c\x6c\x6f\x20\x57\x6f\x72\x6c'
                 b'\x64\x71\x3e\x03')
        ]
        mock_socket.send.assert_has_calls(excepted_send_call)

    @patch('socket.socket')
    def test_set_play_list_socket_error(self, mock_socket, dm_client):
        dm_client.sock = None
        result = dm_client.set_play_list(content='')
        assert result == DmReturnCode.SOCKET_ERROR

    @patch('socket.socket')
    def test_set_play_list_timeout(self, mock_socket, dm_client):
        dm_client.sock = mock_socket
        dm_client.sock.recv.side_effect = [
            socket.timeout()
        ]
        result = dm_client.set_play_list(content='')
        assert result == DmReturnCode.HOST_RESPONSE_TIMEOUT

    @patch('socket.socket')
    def test_set_play_list_protocol_parser_error(self, mock_socket, dm_client):
        dm_client.sock = mock_socket
        dm_client.sock.recv.side_effect = [
            b'\x02\x30\x31\x30\x31\x37\x32\x31\x16\x16\x03'
        ]
        result = dm_client.set_play_list(content='')
        assert result == DmReturnCode.PROTOCOL_PARSER_ERROR

    @patch('socket.socket')
    def test_set_play_list_host_response_error(self, mock_socket, dm_client):
        dm_client.sock = mock_socket
        response = b'\x30\x31\x30\x30\x37\x32\x30'
        cp = CrcUtils.DianMing_crc_16_table(response)
        response = b'\x02' + response + cp.get_bytes() + b'\x03'
        dm_client.sock.recv.side_effect = [
            response
        ]
        result = dm_client.set_play_list(content='')
        assert result == DmReturnCode.HOST_RESPONSE_ERROR

    @patch('socket.socket')
    def test_set_play_list_client_request_error(self, mock_socket, dm_client):
        dm_client.sock = mock_socket
        response = b'\x30\x31\x30\x30\x37\x32\x36'
        cp = CrcUtils.DianMing_crc_16_table(response)
        response = b'\x02' + response + cp.get_bytes() + b'\x03'
        dm_client.sock.recv.side_effect = [
            response
        ]
        result = dm_client.set_play_list(content='')
        assert result == DmReturnCode.CLIENT_REQUEST_ERROR

    @patch('socket.socket')
    def test_set_play_list_UNKNOWN_ERROR(self, mock_socket, dm_client):
        dm_client.sock = mock_socket
        response = b'\x30\x31\x30\x30\x37\x32\x37'
        cp = CrcUtils.DianMing_crc_16_table(response)
        response = b'\x02' + response + cp.get_bytes() + b'\x03'
        dm_client.sock.recv.side_effect = [
            response
        ]
        result = dm_client.set_play_list(content='')
        assert result == DmReturnCode.UNKNOWN_ERROR

    @patch('socket.socket')
    def test_get_now_play_content_success(self, mock_socket, dm_client):
        dm_client.sock = mock_socket
        dm_client.sock.recv.side_effect = [
            b'\x02\x30\x31\x30\x30\x37\x34\x30\x30\x30\x30\x30\x30\x33\x30\x30\x30\x30\x30\x30\x30\x30\x30\x5c\x43'
            b'\x30\x30\x30\x30\x30\x30\x5c\x46\x73\x33\x32\x33\x32\x5c\x54\x32\x35\x35\x30\x30\x30\x30\x30\x30\x30'
            b'\x30\x30\x5c\x4b\x30\x30\x30\x30\x30\x30\x30\x30\x30\x30\x30\x30\x5c\x57\x48\x65\x6c\x6c\x6f\x20\x57'
            b'\x6f\x72\x6c\x64\x24\xca\x03'
        ]
        result = dm_client.get_now_play_content()
        assert result == r'\C000000\Fs3232\T255000000000\K000000000000\WHello World'

        # 测试发送报文正确性
        excepted_send_call = [
            call(b'\x02\x30\x30\x30\x31\x37\x33\x67\x2C\x03')
        ]
        mock_socket.send.assert_has_calls(excepted_send_call)


if __name__ == '__main__':
    pytest.main([__file__])
