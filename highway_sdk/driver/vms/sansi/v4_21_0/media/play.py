#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:FileName: play.py
:Project:
:Brand:
:Version:
:Description: 
:Author: He YinYu
:Link:
:Time: 2025/4/16 16:34
"""
from typing import List

from pydantic import BaseModel

from .win import Win


class Play(BaseModel):
    pass


class MultipleWinPlay(Play):
    """
    多窗口 playlist
    """

    win_list: List[Win]

    def __str__(self):
        line_break = "\r\n"
        protocol = "[playlist]"
        protocol += line_break
        protocol += f"nwindows={len(self.win_list)}"
        protocol += line_break
        for i, win in enumerate(self.win_list):
            protocol += f'windows{i}_x={win.x}'
            protocol += line_break
            protocol += f'windows{i}_y={win.y}'
            protocol += line_break
            protocol += f'windows{i}_w={win.w}'
            protocol += line_break
            protocol += f'windows{i}_h={win.h}'
            protocol += line_break
            protocol += f"{win}"

        return protocol


class SingleWinPlay(Play):
    """
    单窗口 playlist
    """

    win: Win

    def __str__(self):
        line_break = "\r\n"
        protocol = "[playlist]"
        protocol += line_break
        protocol += f"{self.win}"

        return protocol


