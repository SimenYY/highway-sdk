#!/usr/bin/env python
# -*- coding: utf-8 -*-


from .baseMedia import BaseMedia


class TextMedia(BaseMedia):

    font: str
    text_size: int
    text_color: str
    background_color: str
    text: str
    flash: str
    font_style: int
    world_space: int
    alignment_direction: int

    def create_msg(self) -> str:
        protocol_1: str = (f'txt{self.index}='
                           f'{self.x},'
                           f'{self.y},'
                           f'{self.font},'
                           f'{self.text_size},'
                           f'{self.text_color},'
                           f'{self.background_color},'
                           f'{self.flash},'
                           f'{self.text},'
                           f'{self.width},'
                           f'{self.height},'
                           f'{self.font_style}')

        protocol_2: str = (f'txtparam{self.index}='
                           f'{self.world_space},'
                           f'{self.alignment_direction}')

        return protocol_1 + '\n' + protocol_2
