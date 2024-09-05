#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:FileName: test_play.py
:Project:
:Brand:
:Version:
:Description: 
:Author: He YinYu
:Link:
:Time: 2024/8/22 17:20
"""
import pytest
from highway_sdk.vms.SanSi.v4_21_0.media import MediaBuilder, ItemBuilder, PlayBuilder, WinBuilder


class TestPlayBuilder:

    @pytest.fixture
    def media_builder(self):
        media_builder = MediaBuilder()
        media_builder.x = 48
        media_builder.y = 8
        media_builder.text_size = 32
        media_builder.text_color = '255000000000'
        media_builder.font = 'k'
        media_builder.text = 'hi, 你好'
        media_builder.word_space = 5

        return media_builder

    @pytest.fixture
    def item_builder(self, media_builder):
        item_builder = ItemBuilder()
        item_builder.duration = 200
        item_builder.add_media_builder(media_builder)
        return item_builder

    def test_media_create_msg_by_text(self, media_builder):
        excepted_msg = r'\C048008\fk3232\c255000000000\S05hi, 你好'
        assert media_builder.build().create_msg() == excepted_msg

    def test_media_create_msg_by_image(self):
        media_builder = MediaBuilder()
        media_builder.bmp_file_name = '003'

        expected_msg = r'\B003'
        assert media_builder.build().create_msg() == expected_msg

    def test_item_create_msg(self, item_builder):
        expected_msg = r'200,1,0,\C048008\fk3232\c255000000000\S05hi, 你好'

        assert item_builder.build().create_msg() == expected_msg

    def test_win_create_msg(self, item_builder):
        win_builder = WinBuilder()
        win_builder.add_item_builder(item_builder)

        expected_msg = r'item_no=1' + '\n'
        expected_msg += r'item0=200,1,0,\C048008\fk3232\c255000000000\S05hi, 你好'

        assert win_builder.build().create_msg() == expected_msg

    def test_play_create_msg_by_multiple_win(self, item_builder):
        play_builder = PlayBuilder()
        win_builder = WinBuilder()
        win_builder.x = 32
        win_builder.y = 0
        win_builder.w = 128
        win_builder.h = 128
        win_builder.add_item_builder(item_builder)
        play_builder.add_win_or_item_builder(win_builder)
        expected_msg = '[playlist]\n'
        expected_msg += 'nwindows=1\n'
        expected_msg += 'windows0_x=32\n'
        expected_msg += 'windows0_y=0\n'
        expected_msg += 'windows0_w=128\n'
        expected_msg += 'windows0_h=128\n'
        expected_msg += r'item_no=1' + '\n'
        expected_msg += r'item0=200,1,0,\C048008\fk3232\c255000000000\S05hi, 你好'

        assert play_builder.build().create_msg() == expected_msg

    def test_play_create_msg_by_single_win(self, item_builder):
        play_builder = PlayBuilder()
        play_builder.add_win_or_item_builder(item_builder)

        expected_msg = '[playlist]\n'
        expected_msg += r'item_no=1' + '\n'
        expected_msg += r'item0=200,1,0,\C048008\fk3232\c255000000000\S05hi, 你好'

        assert play_builder.build().create_msg() == expected_msg


if __name__ == '__main__':
    pytest.main([__file__])
