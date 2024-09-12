#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:FileName: mqtt.py
:Project:
:Brand:
:Version:
:Description: 
:Author: He YinYu
:Link:
:Time: 2024/9/4 10:22
"""
import logging
import random
from datetime import datetime
from typing import List, Dict, Any, Callable
import paho.mqtt.client as mqtt
from loguru import logger
import shortuuid
from ._models import (
    PublishRealMqttModel,
    PublishHistoryModel,
    PublishControlResMqttModel,
    SubscribeControlReqModel
)


class MqttClient:

    def __init__(self,
                 host: str = 'localhost',
                 port: int = 1883,
                 client_id: str | None = None,
                 qos: int = 0):
        self._host = host
        self._port = port
        self._qos = qos
        if client_id is None:
            self._client_id = f'hw-sdk-{shortuuid.ShortUUID().random(length=12)}'
        else:
            self._client_id = client_id

        self._client: mqtt.Client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,
                                                client_id=self._client_id)

        def on_log(client, userdata, paho_log_level, messages):
            match paho_log_level:
                case mqtt.MQTT_LOG_DEBUG:
                    logger.debug(messages)
                case mqtt.MQTT_LOG_INFO:
                    logger.info(messages)
                case mqtt.MQTT_LOG_WARNING:
                    logger.warning(messages)
                case mqtt.MQTT_LOG_ERR:
                    logging.error(messages)
                case _:
                    logger.info(messages)

        self._client.on_log = on_log

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
        return True

    @property
    def log_address(self) -> str:
        return f'{self._host}:{self._port}'

    def connect(self) -> None:
        def on_connect(client, userdata, flags, reason_code, properties):
            if reason_code.is_failure:
                logger.critical(f'Failed to connect {self.log_address}: {reason_code}.')
            else:
                logger.success(f'Connected to MQTT Broker {self.log_address}')

        self._client.on_connect = on_connect
        try:
            self._client.connect(self._host, self._port)
        except ConnectionRefusedError as e:
            logger.error(f'Failed to connect {self.log_address}: {e}')
        # 启动守护线程，主线程退出，则线程退出
        self._client.loop_start()

    def disconnect(self) -> None:
        def on_disconnect(client, userdata, disconnect_flags, reason_code, properties):
            logger.error(f'Disconnected from MQTT Broker {self.log_address}')

        self._client.on_disconnect = on_disconnect
        self._client.disconnect()
        self._client.loop_stop()

    def publish(self, topic: str, payload: str = None, retain: bool = False) -> mqtt.MQTTMessageInfo:
        """

        :param topic:
        :param payload:
        :param retain:
        :return:
        """

        def on_publish(client, userdata, mid, reason_code, properties):
            pass

        self._client.on_publish = on_publish
        return self._client.publish(topic=topic, payload=payload, qos=self._qos, retain=retain)

    def subscribe(
            self,
            topic: str,
            callback: Callable[[mqtt.Client, Any, mqtt.MQTTMessage], None] = None,
    ) -> None:
        """
        回调函数格式
        def on_message(client, userdata, message):
            ...


        :param topic: 订阅主题
        :param callback: 消息回调函数
        :return:
        """

        def on_message(client, userdata, message):
            logger.debug(f'Received "{message.payload}" from "{message.topic}" topic')

        if callback is None:
            self._client.on_message = on_message
        else:
            self._client.on_message = callback

        self._client.subscribe(topic=topic, qos=self._qos)


class IotMqttClient(MqttClient):
    """
    物联智控 mqtt 客户端
    """

    @property
    def formatted_time(self):
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def publish_real_data(
            self,
            series: str,
            sn: str,
            data: dict
    ) -> mqtt.MQTTMessageInfo:
        """
        推送实时数据

        :param series:
        :param sn:
        :param data:
        :return:
        """
        model = PublishRealMqttModel(series=series,
                                     sn=sn,
                                     time=self.formatted_time,
                                     data=data)
        return self.publish(topic=model.getTopic(), payload=model.getPayload())

    def subscribe_control_req(
            self,
            series: str,
            sn: str,
            on_message: Callable[[mqtt.Client, Any, mqtt.MQTTMessage], None]
    ) -> None:
        """
        订阅控制主题

        :param series:
        :param sn:
        :param on_message:
        :return:
        """
        topic = SubscribeControlReqModel.getTopic(series=series, sn=sn)
        return self.subscribe(topic=topic, callback=on_message)

    def publish_control_res(
            self,
            series: str,
            sn: str,
            sequence: int,
            data: Dict[str, PublishControlResMqttModel.InnerData]
    ) -> mqtt.MQTTMessageInfo:
        """
        推送控制响应

        :param series:
        :param sn:
        :param sequence:
        :param data:
        :return:
        """
        model = PublishControlResMqttModel(series=series,
                                           sn=sn,
                                           time=self.formatted_time,
                                           sequence=sequence,
                                           data=data)
        return self.publish(topic=model.getTopic(), payload=model.getPayload())

    def publish_history_data(
            self,
            series: str,
            sn: str,
            data: List[PublishHistoryModel.InnerData]
    ) -> mqtt.MQTTMessageInfo:
        """
        推送历史数据

        :param series:
        :param sn:
        :param data:
        :return:
        """
        model = PublishHistoryModel(series=series,
                                    sn=sn,
                                    time=self.formatted_time,
                                    data=data)
        return self.publish(topic=model.getTopic(), payload=model.getPayload())
