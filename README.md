# highway_sdk
# 介绍
本项目主要作用是作为公路交通领域，机电设备、智能设备等设备协议SDK封装，方便开发者统一用Python快速建立起对设备的交互

项目地址：http://172.16.1.53/supconit/highway_sdk.git

库地址：http://172.20.61.88:8080/simple/highway-sdk/

## 打包
### 使用setup
```bash
python setup.py sdist bdist_wheel
```
### 使用poetry
```bash
poetry build
```
## 上传
### 使用poetry
```bash
poetry config repositories.private http://172.20.61.88:8080/
poetry publish --repository private
```
## 本地安装
```bash
pip install highway_sdk -i http://172.20.61.88:8080/simple/ --trusted-host 172.20.61.88
```
## 在线安装
```bash
pip install highway_sdk
```
## 更新
```bash
poetry update
```
# 快速浏览
1. VMS 情报板
   1. 诺瓦
      1. 功能：
         1. 查询当前播放节目
         2. 查询当前所有播放节目
         3. 发送并播放节目
         4. 查询设备点阵大小
   2. 电明
      1. 功能
         1. 查询当前播放节目
         2. 发送并播放节目
   3. 三思
      1. 功能
         1. 查询当前播放节目
         2. 发送并播放节目
2. 平台接口
   1. 物联智控 & MQTT
# SDK使用说明
## VMS 情报板
### 诺瓦 Nova
在线文档：https://docapi.vnnox.com/web/#/20?page_id=2289
#### 发送节目
```python 
from highway_sdk.vms.nova.v3_11_5.internet.novaClient import NovaClient
from highway_sdk.vms.nova.v3_11_5.media import PlayBuilder, ItemBuilder, TextPlusMediaBuilder

# 发送播放表
with NovaClient("localhost") as client:
    # 创建媒体
    text_plus_builder = TextPlusMediaBuilder()
    text_plus_builder.text = "hello world"

    # 先获取屏幕点阵参数
    ret = client.get_device_size()
    if ret is not None:
        w, h = ret
        text_plus_builder.width = w
        text_plus_builder.height = h

    # 创建页面item
    item_builder = ItemBuilder()
    item_builder.add_media_builder(text_plus_builder)

    # 创建播放表
    play_builder = PlayBuilder()
    play_builder.add_item_builder(item_builder)

    # 生成播放表内容， 设置播放表，
    content = play_builder.set_play_id(1).build().create_msg()

    client.set_play_list(content)


```
#### 查询设备点阵大小
```python
from highway_sdk.vms.nova.v3_11_5.internet.novaClient import NovaClient

with NovaClient("localhost") as client:
    w, h = client.get_device_size
```
#### 查询当前页面
```python
from highway_sdk.vms.nova.v3_11_5.internet.novaClient import NovaClient

with NovaClient('127.0.0.1') as client:
    # 直接返回数据域内容
    data = client.get_now_play_content()
    if data is not None:
        # todo 近一步解析数据域
        pass
```
### 查询当前所有播放节目
```python
from highway_sdk.vms.nova.v3_11_5.internet.novaClient import NovaClient

with NovaClient('127.0.0.1') as client:
    play_list = client.get_now_play_all_content()
```
### 电明 DianMing
#### 发送节目
```python
from highway_sdk.vms.DianMing.v2_3_0.internet.dmClient import DmClient
from highway_sdk.vms.DianMing.v2_3_0.media import PlayBuilder, ItemBuilder, MediaBuilder
from highway_sdk.vms.DianMing.v2_3_0.media.enums import FontEnum, ColorEnum

with DmClient("localhost") as cli:
    # 创建媒体
    media = MediaBuilder()
    media.x = 0
    media.y = 0
    # 推荐用标准的枚举类型，下同
    media.font = FontEnum.SONG_TI.value
    media.text_size = 32
    media.text_color = ColorEnum.GREEN.value
    media.background_color = ColorEnum.BLACK.value
    media.text = 'Hello World'

    item = ItemBuilder()
    item.duration = 30
    item.add_media_builder(media)

    play = PlayBuilder()
    content = play.add_item_builder(item).build().create_msg()
    
    cli.set_play_list(content)

```
#### 查询当前页面

```python
from highway_sdk.vms.DianMing.v2_3_0.internet.dmClient import DmClient

with DmClient('localhost') as cli:
    current_item = cli.get_now_play_content()
    # todo 解析处理，推荐用正则
    pass

# 如果使用自己的通信框架，可以使用protocol简化报文部分的代码
from highway_sdk.vms.DianMing.v2_3_0.internet.protocol import Protocol
from highway_sdk.vms.DianMing.v2_3_0.internet.utils.constants import DmWhat
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.send(Protocol.get_now_play_content())
recv = sock.recv(1024)
data = Protocol.Parser(recv, DmWhat.GET_NOW_PLAY_CONTENT_RSP)
# todo 近一步处理...
```
### 三思 SanSi
#### 发送节目
```python
from highway_sdk.vms.SanSi.v4_21_0.media import PlayBuilder, ItemBuilder, WinBuilder, MediaBuilder
from highway_sdk.vms.SanSi.v4_21_0.internet.sanSiClient import SanSiClient

with SanSiClient("localhost") as client:
    # 单窗口播放
    media_builder = MediaBuilder()
    media_builder.text = "hello world"
    
    item_builder = ItemBuilder()
    item_builder.add_media_builder(media_builder)
    item_builder.duration = 300
    
    play_builder = PlayBuilder()
    play_builder.add_win_or_item_builder(item_builder)
    
    content = play_builder.build().create_msg()
    
    client.set_play_list(content)
    
    # 多窗口播放
    media_builder = MediaBuilder()
    media_builder.text = "hello world"
    
    item_builder = ItemBuilder()
    item_builder.add_media_builder(media_builder)
    item_builder.duration = 300
    
    # 窗口1
    win_builder_1 = WinBuilder()
    win_builder_1.add_item_builder(item_builder)
    win_builder_1.x = 0
    win_builder_1.y = 0
    win_builder_1.w = 100
    win_builder_1.h = 100
    
    # 窗口2 相同内容
    win_builder_2 = WinBuilder()
    win_builder_2.add_item_builder(item_builder)
    win_builder_2.x = 100
    win_builder_2.y = 100
    win_builder_2.w = 100
    win_builder_2.h = 100
    
    
    play_builder = PlayBuilder()
    play_builder.add_win_or_item_builder(win_builder_1).add_win_or_item_builder(win_builder_2)
    
    content = play_builder.build().create_msg()
```
#### 查询当前页面
```python
from highway_sdk.vms.SanSi.v4_21_0.internet.sanSiClient import SanSiClient
with SanSiClient('localhost') as client:
    data = client.get_now_play_content()
    # todo 解析data
    pass
```
## 平台接口
### 物联智控 & MQTT
使用with

发布
```python
import time
from highway_sdk.interface.iot.mqttClient import MqttClient, IotMqttClient

# 支持with
with IotMqttClient() as client:
    while True:
        client.publish_real_data(series='vms', sn='vms_127.0.0.1', data={'test': 'test'})
        time.sleep(1)
```
订阅
```python
import time
from highway_sdk.interface.iot.mqttClient import MqttClient, IotMqttClient


def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))


with MqttClient() as client:
    while True:
        client.subscribe('test/', on_message)
        time.sleep(1)
```
嵌入到你的代码里
```python
import time
from highway_sdk.interface.iot.mqttClient import MqttClient, IotMqttClient

cli = IotMqttClient()
cli.connect()

cli.publish_real_data(series='vms', sn='vms_127.0.0.1', data={'test': 'test'})

# 断开
cli.disconnect()
```

