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
from datetime import datetime
from typing import List, Dict, Any
import uuid
import paho.mqtt.client as mqtt
from loguru import logger

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
        self.mqtt_host = host
        self.mqtt_port = port
        self.qos = qos
        if client_id is None:
            self.client_id = f'mqtt_client_{uuid.uuid4()}'
        else:
            self.client_id = client_id

        self._client: mqtt.Client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,
                                                client_id=self.client_id)

        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect
        self._client.on_publish = self._on_publish
        self._client.on_subscribe = self._on_subscribe
        self._client.on_log = self._on_log

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
        # 抑制异常
        return True

    def log_address(self) -> str:
        return f'{self.mqtt_host}:{self.mqtt_port}'

    def connect(self) -> None:
        # try:
        #     self._client.connect(self.mqtt_host, self.mqtt_port)
        # except ConnectionRefusedError as e:
        #     logger.error(f'Failed to connect to MQTT Broker {self.log_address()}: {e}')

        # 连接在后台进行
        self._client.connect_async(self.mqtt_host, self.mqtt_port)
        self._client.loop_start()

    def disconnect(self) -> None:
        self._client.disconnect()
        self._client.loop_stop()

    def publish(
            self,
            topic: str,
            payload: str = None,
            retain: bool = False
    ) -> mqtt.MQTTMessageInfo:
        """

        :param topic:
        :param payload:
        :param qos:
        :param retain:
        :return:
        """
        return self._client.publish(topic=topic,
                                    payload=payload,
                                    qos=self.qos,
                                    retain=retain)

    def subscribe(
            self,
            topic: str,
    ) -> tuple[int, int]:
        """

        :param topic:
        :return:
        """
        return self._client.subscribe(topic=topic,
                                      qos=self.qos)

    # def loop_forever(
    #         self,
    #         timeout: float = 1.0,
    #         retry_first_connection: bool = False,
    # ) -> int:
    #     return self._client.loop_forever(timeout=timeout,
    #                                      retry_first_connection=retry_first_connection)

    def _on_connect(self, client, userdata, flags, reason_code, properties):
        """

        :param client:
        :param userdata:
        :param flags:
        :param reason_code:
        :param properties:
        :return:
        """
        if reason_code.is_failure:
            logger.error(f'Failed to connect {self.log_address()}: {reason_code}.')
        else:
            logger.info(f'Connected to MQTT Broker {self.log_address()}')

    def _on_disconnect(self, client, userdata, disconnect_flags, reason_code, properties):
        """

        :param client:
        :param userdata:
        :param disconnect_flags:
        :param reason_code:
        :param properties:
        :return:
        """
        logger.error(f'Disconnected from MQTT Broker {self.log_address()}')

    @staticmethod
    def _on_subscribe(client, userdata, mid, reason_code_list, properties):
        """

        :param client:
        :param userdata:
        :param mid:
        :param reason_code_list:
        :param properties:
        :return:
        """
        pass

    @staticmethod
    def _on_message(client, userdata, msg):
        """
        收到订阅主题的消息

        :param client:
        :param userdata:
        :param msg:
        :return:
        """
        logger.debug(f'topic: {msg.topic}, payload: {msg.payload}')

    @staticmethod
    def _on_publish(client, userdata, mid, reason_code, properties):
        """
        发布消息成功回调

        :param client:
        :param userdata:
        :param mid:
        :param reason_code:
        :param properties:
        :return:
        """
        pass

    @staticmethod
    def _on_log(client, userdata, paho_log_level, messages):
        """

        :param client:
        :param userdata:
        :param paho_log_level:
        :param messages:
        :return:
        """
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
            sn: str
    ) -> tuple[Any, int | None]:
        """
        订阅控制主题

        :param series:
        :param sn:
        :return:
        """
        topic = SubscribeControlReqModel.getTopic(series=series, sn=sn)
        return self.subscribe(topic=topic)

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
