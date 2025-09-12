#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .baseMedia import BaseMedia
from .enums import FontEnum, FontStyleEnum, ColorEnum
from pydantic import Field, field_validator


class TextMedia(BaseMedia):
    font: FontEnum
    text_size: int
    text_color: ColorEnum
    background_color: ColorEnum
    text: str
    flash: str
    font_style: FontStyleEnum
    world_space: int = Field(..., ge=0, le=100)
    alignment_direction: int

    @field_validator("text_size")
    @classmethod
    def validate_text_size(cls, value: int):
        value_str = str(value)
        length = len(value_str)
        half_len = int(length / 2)
        if length % 2 != 0:
            raise ValueError("Text size 格式不正确，e.g. 1616， 2424")
        elif value_str[:half_len] != value_str[half_len:]:
            raise ValueError("Text size 格式不正确，e.g. 1616， 2424")
        else:
            return value

    def create_msg(self) -> str:
        protocol_1: str = (
            f"txt{self.index}="
            f"{self.x},"
            f"{self.y},"
            f"{self.font.value},"
            f"{self.text_size},"
            f"{self.text_color.value},"
            f"{self.background_color.value},"
            f"{self.flash},"
            f"{self.text},"
            f"{self.width},"
            f"{self.height},"
            f"{self.font_style.value}"
        )

        protocol_2: str = (
            f"txtparam{self.index}={self.world_space},{self.alignment_direction}"
        )

        return protocol_1 + "\n" + protocol_2
