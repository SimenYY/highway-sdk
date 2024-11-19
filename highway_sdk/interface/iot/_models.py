#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:FileName: model.py
:Project:
:Brand:
:Version:
:Description: 
:Author: He YinYu
:Link:
:Time: 2024/9/4 10:25
"""
import json
from dataclasses import dataclass, asdict
from typing import Dict, List

from pydantic import BaseModel


@dataclass
class MqttModel:
    def toDict(self) -> dict:
        """
        类成员转字典形式

        :return:
        """
        return asdict(self)

    def getPayload(self) -> str:
        return json.dumps(self.toDict())

    def getTopic(self) -> str:
        """
        获取对应主题
        :return:
        """
        pass


class SubscribeControlReqModel(BaseModel):
    """
    设备订阅接受控制命令, 用于校验

    :ivar series: 设备产品序列号
    :ivar sn: 设备标识码
    :ivar version: 设备版本号
    :ivar time: 推送时间
    :ivar needResponse: 是否需要设备响应控制命令
    :ivar sequence: 命令序列号
    :ivar data: 可下发单条或者多条控制命令
    """
    series: str
    sn: str
    version: str
    time: str
    needResponse: bool
    sequence: int
    data: dict

    @staticmethod
    def getTopic(series: str, sn: str, version: str = 1.0) -> str:
        return f'/edge/{series}/{sn}/{version}/control'


@dataclass
class PublishControlResMqttModel(MqttModel):
    """
    设备响应控制命令

    :ivar series: 设备产品序列号
    :ivar sn: 设备标识码
    :ivar version: 设备版本号
    :ivar time: 推送时间
    :ivar sequence: 命令序列号
    :ivar data: 可下发单条或者多条控制命令

    注：（必填）data.time、data.value、data.succes、data.resultcode
              data.resultMsg
    """

    @dataclass
    class InnerData:
        time: str
        value: str | bool | int | float
        succes: bool
        resultCode: int
        resultMsg: str

    series: str
    sn: str
    time: str
    sequence: int
    data: Dict[str, InnerData]
    version: str = '1.0'

    def getTopic(self) -> str:
        return f'/edge/{self.series}/{self.sn}/{self.version}/response'


@dataclass
class PublishRealMqttModel(MqttModel):
    """
    设备推送实时数据

    :ivar series: 设备产品序列号
    :ivar sn: 设备标识码
    :ivar version: 设备版本号
    :ivar time: 推送时间 (yyyy-MM-dd HH:mm:ss)
    :ivar data: 可下发单条或者多条实时数据
    """
    series: str
    sn: str
    time: str
    data: dict
    version: str = '1.0'

    def getTopic(self):
        return f'/edge/{self.series}/{self.sn}/{self.version}/data'


@dataclass
class PublishHistoryModel(MqttModel):
    """
    设备推送历史数据

    :ivar series: 设备产品序列号
    :ivar sn: 设备标识码
    :ivar version: 设备版本号
    :ivar time: 推送时间
    :ivar data: 可下发单条或者多条历史数据,

    注：（必填）data.time
    """

    class InnerData:
        def __init__(self, time: str, **kwargs):
            self.time = time

            for k, v in kwargs.items():
                setattr(self, k, v)

    series: str
    sn: str
    time: str
    data: List[InnerData]
    version: str = '1.0'

    def getTopic(self):
        return f'/edge/{self.series}/{self.sn}/{self.version}/history'