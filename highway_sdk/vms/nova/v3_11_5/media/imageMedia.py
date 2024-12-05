#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:FileName: imageMedia.py
:Project:
:Brand:
:Version:
:Description: 
:Author: He YinYu
:Link:
:Time: 2024/9/3 15:35
"""
from .baseMedia import BaseMedia


class ImageMedia(BaseMedia):
    file_path: str
    flash: str

    def create_msg(self):
        protocol_1 = (f'img{self.index}='
                      f'{self.x},'
                      f'{self.y},'
                      f'{self.file_path},'
                      f'{self.flash},'
                      f'{self.width},'
                      f'{self.height}')
        protocol_2 = (f'imgparam{self.index}='
                      f'{self.duration},'
                      f'0,'  # 占位符
                      f'00,'  # 动画类型
                      f'1,'  # 播放次数
                      f'1')  # 动画时长
        return protocol_1 + '\n' + protocol_2
