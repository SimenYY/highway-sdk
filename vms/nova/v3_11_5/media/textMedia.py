#!/usr/bin/env python
# -*- coding: utf-8 -*-


from .baseMedia import BaseMedia


class TextMedia(BaseMedia):

    def __init__(self, builder):
        super().__init__(builder)

        self.font = builder.font
        self.text_size = builder.text_size
        self.text_color = builder.text_color
        self.background_color = builder.background_color
        self.text = builder.text
        self.flash = builder.flash
        self.font_style = builder.font_style
        self.world_space = builder.world_space
        self.alignment_direction = builder.alignment_direction

    def create_protocol(self) -> str:
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
