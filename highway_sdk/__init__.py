#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from platformdirs import PlatformDirs
from ._version import __version__


__name__ = "highway-sdk"
__all__ = ["__version__", "__name__"]


logger = logging.getLogger(__name__)

dirs = PlatformDirs(appauthor=__name__)
