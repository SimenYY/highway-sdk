#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import List, Optional

from .media.playBuilder import PlayBuilder
from .internet.novaClient import NovaClient


class PlayManager:

    def __init__(self, play_builder: PlayBuilder, nova_client: NovaClient):
        if not isinstance(nova_client, NovaClient):
            raise TypeError("nova_client must be of type NovaClient")

        if not isinstance(play_builder, PlayBuilder):
            raise TypeError("play_builder must be of type PlayBuilder")

        # 上传文件集合, 暂时不用
        self.play_list: List[str] = []
        # 节目build对象
        self._play_builder: PlayBuilder = play_builder
        # nova 通信对象
        self._nova_client = nova_client

    def __get_play_id(self) -> int:
        return self._play_builder.build().play_id

    def play(self) -> int:
        content = self._play_builder.build().__str__()
        play_id = self.__get_play_id()
        ret = self._nova_client.set_play_list(content, play_id)

        return ret
