#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pydantic import BaseModel, NonNegativeInt
from typing import List
from .baseMedia import BaseMedia


class Item(BaseModel):
    """
    表示每一个页面（播放项）
    """
    media_list: List[BaseMedia]
    duration: NonNegativeInt
    auto_media_index: NonNegativeInt
    index: NonNegativeInt
    screen_in: str
    screen_out: str
    screen_speed: str
    flash_speed: str
    flash_count: str
    play_count: str

    def create_msg(self) -> str:
        protocol = [f'[item{self.index}]', '\n']
        param = (f"param={self.duration},"
                 f"{self.screen_in},"
                 f"{self.screen_out},"
                 f"{self.screen_speed},"
                 f"{self.flash_speed},"
                 f"{self.flash_count},"
                 f"{self.play_count}")
        protocol.append(param)
        protocol.append('\n')

        for media in self.media_list:
            protocol.append(media.create_msg())
            protocol.append('\n')

        return ''.join(protocol[:-1])  # 删除最后一个'\n'
