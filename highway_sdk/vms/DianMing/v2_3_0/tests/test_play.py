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
:Time: 2024/8/21 9:37
"""
import pytest
from highway_sdk.vms.DianMing.v2_3_0.media.playBuilder import PlayBuilder
from highway_sdk.vms.DianMing.v2_3_0.media.itemBuilder import ItemBuilder
from highway_sdk.vms.DianMing.v2_3_0.media.mediaBuilder import MediaBuilder
from highway_sdk.vms.DianMing.v2_3_0.media.enums import FontEnum, ColorEnum


class TestPlayBuilder:

    def setup_method(self, method):
        self.media = MediaBuilder()
        self.media.x = 0
        self.media.y = 0
        self.media.font = FontEnum.SONG_TI.value
        self.media.text_size = 32
        self.media.text_color = ColorEnum.GREEN.value
        self.media.background_color = ColorEnum.BLACK.value
        self.media.text = 'Hello World'

    def test_media_create_msg(self):
        msg = self.media.build().create_msg()

        expected_msg = r'\C000000\Fs3232\T000255000000\K000000000000\WHello World'

        assert msg == expected_msg

    def test_item_create_msg(self):
        item = ItemBuilder()
        item.duration = 30
        msg = item.add_media_builder(self.media).build().create_msg()

        expected_msg = r'30,0,0,0,0,\C000000\Fs3232\T000255000000\K000000000000\WHello World'
        assert msg == expected_msg

    def test_play_create_msg(self):
        item = ItemBuilder()
        item.duration = 30
        item.add_media_builder(self.media)

        play = PlayBuilder()
        msg = play.add_item_builder(item).build().create_msg()

        expected_msg = '[PLAYLIST]'
        expected_msg += '\n'
        expected_msg += 'ITEM_NO=001'
        expected_msg += '\n'
        expected_msg += r'ITEM000=30,0,0,0,0,\C000000\Fs3232\T000255000000\K000000000000\WHello World'
        # print('msg', msg)
        # print('expected_msg', expected_msg)
        assert msg == expected_msg


if __name__ == '__main__':
    pytest.main([__file__])
