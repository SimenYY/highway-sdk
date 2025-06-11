#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:FileName: aTask.py
:Project:
:Brand:
:Version:
:Description: 
:Author: He YinYu
:Link:
:Time: 2025/1/13 14:30
"""
import asyncio
import random

from dataclasses import dataclass
from typing import Optional, Callable


@dataclass
class LoopingCallTask:
    """
    Task must be non-blocking
    """
    task: Callable[[], None]

    jitter: float = 0.119626565582
    is_jittery: bool = False

    _task_handle: Optional[asyncio.TimerHandle] = None
    _loop: Optional[asyncio.AbstractEventLoop] = None

    @property
    def loop(self) -> asyncio.AbstractEventLoop:
        if self._loop is None:
            self._loop = asyncio.get_running_loop()
        return self._loop

    def start(self, interval: float, soon: bool = False) -> None:
        if interval < 0:
            raise ValueError('interval must be >= 0')

        if self.is_jittery:
            jittery = random.normalvariate(interval, self.jitter * interval)
        else:
            jittery = interval

        def run_task():
            self.task()
            self._task_handle = self.loop.call_later(jittery, run_task)

        if soon:
            self._task_handle = self.loop.call_later(0, run_task)
        else:
            self._task_handle = self.loop.call_later(jittery, run_task)

    def stop(self) -> None:
        if self._task_handle is not None:
            self._task_handle.cancel()
            self._task_handle = None
        else:
            raise RuntimeError('Task handle is None.')
