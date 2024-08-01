#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:FileName: playManager.py
:Project:
:Brand:
:Version:
:Description: 
:Author: He YinYu
:Link:
:Time: 2024/7/31 19:28
:Department: 公路机电工程技术中心
:Copyright: ©1993-2023 浙江中控信息产业股份有限公司
"""
from typing import List, Optional

from .media.playBuilder import PlayBuilder
from .internet.novaTraffic import NovaTraffic


class PlayManager:
    def __init__(self, play_builder: PlayBuilder, nova_traffic: NovaTraffic):
        # 上传文件集合, 暂时不用
        self.play_list: List[str] = []
        # 节目build对象
        self._play_builder: PlayBuilder = play_builder
        # nova 通信对象
        self._nova_traffic: NovaTraffic = nova_traffic

    def get_play_id(self) -> int:
        return self._play_builder.build().play_id

    def play(self) -> int:
        content = self._play_builder.build().create_protocol()
        play_id = self.get_play_id()
        ret = self._nova_traffic.send_play_list(content, play_id)

        return ret
