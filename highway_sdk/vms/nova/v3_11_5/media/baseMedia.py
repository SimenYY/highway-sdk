#!/usr/bin/env python
# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod


class BaseMedia(ABC):

    def __init__(self, builder):
        self.index: int = builder.index
        self.x: int = builder.x
        self.y: int = builder.y
        self.width: int = builder.width
        self.height: int = builder.height
        self.duration: int = builder.duration

    @abstractmethod
    def __str__(self):
        pass
