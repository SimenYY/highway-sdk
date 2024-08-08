#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Item:
    """
    表示每一个页面（播放项）
    """

    def __init__(self, builder):
        self.media_list = builder.media_list
        self.duration = builder.duration
        self.index = builder.index
        self.screen_in = builder.screen_in
        self.screen_out = builder.screen_out
        self.screen_speed = builder.screen_speed
        self.flash_speed = builder.flash_speed
        self.flash_count = builder.flash_count
        self.play_count = builder.play_count

    def __str__(self) -> str:
        param = (f"param={self.duration},"
                 f"{self.screen_in},"
                 f"{self.screen_out},"
                 f"{self.screen_speed},"
                 f"{self.flash_speed},"
                 f"{self.flash_count},"
                 f"{self.play_count}")

        protocol = [param, '\n']

        for media in self.media_list:
            protocol.append(media.__str__())
            protocol.append('\n')

        return ''.join(protocol[:-1])  # 删除最后一个'\n'

