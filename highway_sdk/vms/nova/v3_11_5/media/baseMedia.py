#!/usr/bin/env python
# -*- coding: utf-8 -*-

from abc import abstractmethod
from pydantic import BaseModel, NonNegativeInt


class BaseMedia(BaseModel):
    index: NonNegativeInt
    x: NonNegativeInt
    y: NonNegativeInt
    width: NonNegativeInt
    height: NonNegativeInt
    duration: NonNegativeInt

    @abstractmethod
    def create_msg(self):
        pass

