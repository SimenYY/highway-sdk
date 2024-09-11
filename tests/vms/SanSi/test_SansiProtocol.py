#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:FileName: test_SansiProtocol.py
:Project:
:Brand:
:Version:
:Description: 
:Author: He YinYu
:Link:
:Time: 2024/9/11 10:04
"""
from unittest.mock import patch

import pytest

from highway_sdk.vms.SanSi.v4_21_0.internet.protocol import Protocol


class TestProtocol:

    @pytest.fixture
    def setup_test_data(self):
        return [
            {
                'input': b'\x02\x30\x31\x30\x30\x30\x30\x30\x35\x30\x30\x30\x31\x30\x30\x30\x30\x30\x5C\x66\x73\x32'
                         b'\x34\x32\x34\x5C\x63\x30\x30\x30\x32\x35\x35\x30\x30\x30\x30\x30\x30\xCB\xED\xB5\xC0\xC2'
                         b'\xB7\xB6\xCE\x5C\x6E\xBD\xF7\xC9\xF7\xBC\xDD\xCA\xBB\xE7\x4F\x03',
                'expected': {
                    'raw_str': '000005000100000\\fs2424\\c000255000000隧道路段 谨慎驾驶',
                    'font': 's',
                    'font_height': '24',
                    'font_width': '24',
                    'text_color': '000255000000',
                    'text': '隧道路段 谨慎驾驶',
                    'image_type': None,
                    'image_name': None,
                },
            },
        ]

    def test_parser_now_play_content(self, setup_test_data):
        for case in setup_test_data:
            result = Protocol.parser_now_play_content(case['input'])
            assert result == case['expected']

    def test_specific_brightness_value(self):
        # 测试亮度值为 15 时的情况
        brightness = 15
        packet = Protocol.set_now_brightness(brightness)
        assert packet == b'\x02\x30\x30\x30\x35\x31\x35\x31\x35\x31\x35\x5E\xA0\x03'


if __name__ == '__main__':
    pytest.main([__file__])
