#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:FileName: test_protocol.py
:Project:
:Brand:
:Version:
:Description: 
:Author: He YinYu
:Link:
:Time: 2024/9/29 10:19
"""
from highway_sdk.core.exceptions import ProtocolParserError
import pytest
from highway_sdk.vms.nova.v3_11_5.internet.protocol import Protocol


class TestProtocol:
    def test_parser_now_play_content_valid_input(self):
        # 构建一个有效的输入缓冲区
        valid_buffer = bytes.fromhex(
            'AA FF FF 2E 01 01 01 5B 69 74 65 6D 31 5D 0A 70 61 72 61 6D 3D 31 30 30 2C 31 2C 31 2C 31 2C 30 2C 35 2C '
            '31 2C 30 2C 31 0A 74 78 74 31 3D 31 30 2C 30 2C 33 2C 31 36 31 36 2C 31 2C 38 2C 30 2C E8 BD A6 E7 89 8C '
            'EF BC 9A E5 86 80 41 33 31 38 41 41 E5 A4 A7 E8 B4 A7 E8 BD A6 2C 31 39 32 2C 33 32 30 2C 30 0A 74 78 74 '
            '70 61 72 61 6D 31 3D 30 2C 30 CC 20 DF')

        expected_output = {
            'raw_str': '10,0,3,1616,1,8,0,车牌：冀A318AA大货车,192,320,0',
            'font': '3',
            'font_size': '1616',
            'text_color': '1',
            'text': '车牌：冀A318AA大货车',
            'image_name': None
        }

        # 测试是否返回正确的字典
        output = Protocol.parser_now_play_content(valid_buffer)
        assert output == expected_output

    def test_parser_now_play_content_invalid_input(self):
        # 构建一个无效的输入缓冲区
        invalid_buffer = b'\x01\x01\x01\x01'

        # 验证是否抛出异常
        with pytest.raises(ProtocolParserError):
            Protocol.parser_now_play_content(invalid_buffer)

    def test_parser_now_brightness_valid_input(self):
        valid_buffer = bytes.fromhex('AA FF FF C3 02 FF CC 3A 2F')
        expected_output = {
            'brightness': 100
        }

        output = Protocol.parser_now_brightness(valid_buffer)
        assert output == expected_output

    def test_parser_now_brightness_invalid_input(self):
        invalid_buffer = b'\x01\x01\x01\x01'

        with pytest.raises(ProtocolParserError):
            Protocol.parser_now_brightness(invalid_buffer)


if __name__ == '__main__':
    pytest.main([__file__])
