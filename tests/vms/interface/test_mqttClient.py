#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:FileName: test_mqttClient.py
:Project:
:Brand:
:Version:
:Description: 
:Author: He YinYu
:Link:
:Time: 2024/9/5 11:29
"""
import pytest
import paho.mqtt.client as mqtt
from unittest.mock import MagicMock, patch
from highway_sdk.interface.iot.mqttClient import MqttClient, IotMqttClient


# 定义一个fixture，用于创建MqttClient实例
@pytest.fixture
def mqtt_client():
    return MqttClient(host='localhost', port=1883)


# 定义一个fixture，用于创建IotMqttClient实例
@pytest.fixture
def iot_mqtt_client():
    return IotMqttClient(host='localhost', port=1883)


# 测试MqttClient的connect方法
def test_mqtt_client_connect(mqtt_client):
    # 使用patch装饰器模拟paho.mqtt.client.Client.connect_async方法
    with patch('paho.mqtt.client.Client.connect_async') as mock_connect:
        # 调用connect方法
        mqtt_client.connect()
        # 验证connect_async方法被正确调用
        mock_connect.assert_called_once_with('localhost', 1883)


# 测试MqttClient的disconnect方法
def test_mqtt_client_disconnect(mqtt_client):
    # 使用patch装饰器模拟paho.mqtt.client.Client.disconnect方法
    with patch('paho.mqtt.client.Client.disconnect') as mock_disconnect:
        # 调用disconnect方法
        mqtt_client.disconnect()
        # 验证disconnect方法被正确调用
        mock_disconnect.assert_called_once()


# 测试MqttClient的publish方法
def test_mqtt_client_publish(mqtt_client):
    # 使用patch装饰器模拟paho.mqtt.client.Client.publish方法
    with patch('paho.mqtt.client.Client.publish') as mock_publish:
        # 调用publish方法
        mqtt_client.publish(topic='test/topic', payload='test payload')
        # 验证publish方法被正确调用
        mock_publish.assert_called_once_with(topic='test/topic', payload='test payload', qos=0, retain=False)


# 测试MqttClient的subscribe方法
def test_mqtt_client_subscribe(mqtt_client):
    # 使用patch装饰器模拟paho.mqtt.client.Client.subscribe方法
    with patch('paho.mqtt.client.Client.subscribe') as mock_subscribe:
        # 调用subscribe方法
        mqtt_client.subscribe(topic='test/topic')
        # 验证subscribe方法被正确调用
        mock_subscribe.assert_called_once_with(topic='test/topic', qos=0)


# 测试IotMqttClient的publish_real_data方法
def test_iot_mqtt_client_publish_real_data(iot_mqtt_client):
    # 使用patch装饰器模拟paho.mqtt.client.Client.publish方法
    with patch('paho.mqtt.client.Client.publish') as mock_publish:
        # 调用publish_real_data方法
        iot_mqtt_client.publish_real_data(series='test_series', sn='test_sn', data={'key': 'value'})
        # 验证publish方法被正确调用
        mock_publish.assert_called_once()


# 测试IotMqttClient的subscribe_control_req方法
def test_iot_mqtt_client_subscribe_control_req(iot_mqtt_client):
    # 使用patch装饰器模拟paho.mqtt.client.Client.subscribe方法
    with patch('paho.mqtt.client.Client.subscribe') as mock_subscribe:
        # 调用subscribe_control_req方法
        iot_mqtt_client.subscribe_control_req(series='test_series', sn='test_sn')
        # 验证subscribe方法被正确调用
        mock_subscribe.assert_called_once()


# 测试IotMqttClient的publish_control_res方法
def test_iot_mqtt_client_publish_control_res(iot_mqtt_client):
    # 使用patch装饰器模拟paho.mqtt.client.Client.publish方法
    with patch('paho.mqtt.client.Client.publish') as mock_publish:
        # 调用publish_control_res方法
        iot_mqtt_client.publish_control_res(series='test_series', sn='test_sn', sequence=1,
                                            data={'key': {'status': 'success', 'value': 'test_value'}})
        # 验证publish方法被正确调用
        mock_publish.assert_called_once()


# 测试IotMqttClient的publish_history_data方法
def test_iot_mqtt_client_publish_history_data(iot_mqtt_client):
    # 使用patch装饰器模拟paho.mqtt.client.Client.publish方法
    with patch('paho.mqtt.client.Client.publish') as mock_publish:
        # 调用publish_history_data方法
        iot_mqtt_client.publish_history_data(series='test_series', sn='test_sn',
                                             data=[{'time': '2024-09-04 10:22:00', 'data': {'key': 'value'}}])
        # 验证publish方法被正确调用
        mock_publish.assert_called_once()


if __name__ == '__main__':
    pytest.main([__file__])
