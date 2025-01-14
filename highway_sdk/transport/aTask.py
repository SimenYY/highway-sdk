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

from typing import Optional, Callable


class LoopingCallTask:
    jitter = 0.119626565582

    def __init__(self, task: Callable[[], None], is_jittery: bool = False,
                 loop: Optional[asyncio.AbstractEventLoop] = None):
        self._task = task
        # 是否需要抖动时间间隔
        self._is_jittery = is_jittery
        self._task_handle: Optional[asyncio.TimerHandle] = None

        if loop is None:
            self.loop = asyncio.get_running_loop()
        else:
            self.loop = loop

    def start(self, interval: float, soon: bool = False):
        if self._task_handle is not None:
            raise RuntimeError('Task is already running')

        if interval < 0:
            raise ValueError('interval must be >= 0')

        if self._is_jittery:
            jittery = random.normalvariate(interval, self.jitter * interval)
        else:
            jittery = interval

        def run_task():
            self._task()
            self._task_handle = self.loop.call_later(jittery, run_task)

        if soon:
            self._task_handle = self.loop.call_soon(run_task)
        else:
            self._task_handle = self.loop.call_later(jittery, run_task)

    def stop(self):
        if self._task_handle is not None:
            self._task_handle.cancel()
            self._task_handle = None

