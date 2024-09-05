#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:FileName: test_playBuilder.py
:Project:
:Brand:
:Version:
:Description: 
:Author: He YinYu
:Link:
:Time: 2024/8/12 15:34
"""
import pytest

from highway_sdk.vms.nova.v3_11_5.media import (
    PlayBuilder,
    ItemBuilder,
    TextPlusMediaBuilder
)

from loguru import logger

logger.remove()


class TestPlayBuilder:
    def test_play_create_msg_test_plus(self):
        play_builder = PlayBuilder()
        item_builder = ItemBuilder()

        text_plus_builder = TextPlusMediaBuilder()

        text_plus_builder.width = 96
        text_plus_builder.height = 56

        text_plus_builder.text = '文本测试'

        item_builder.add_media_builder(text_plus_builder)
        play_builder.add_item_builder(item_builder)

        expected_msg = ('[all]\n'
                        'items=1\n'
                        '[item1]\n'
                        'param=100,1,1,1,0,5,1\n'
                        'txtext1=0,0,96,56,1,1616,0,0,0,1,0,1,8,0,2,100,1,文本测试,0,0,0,5,5,5')
        # print('-----tested-----\n', play_builder.build().create_msg())
        # print('-----expected-----\n', expected_msg)
        assert play_builder.build().create_msg() == expected_msg

    # def test_play_create_msg_text(self):
    #     pass


if __name__ == '__main__':
    # pytest.main(['--html=./test_playBuilder.html', 'test_playBuilder.py'])
    pytest.main([__file__])
