# highway_sdk
# 介绍
本项目主要作用是作为公路交通领域，机电设备、智能设备等设备协议SDK封装，方便开发者统一用Python快速建立起对设备的交互
# SDK使用说明
## VMS 情报板
### Nova
```python
from highway_sdk.vms.nova.v3_11_5.internet.novaClient import NovaClient
from highway_sdk.vms.nova.v3_11_5.media import PlayBuilder, ItemBuilder, TextPlusMediaBuilder

# 创建媒体
text_plus_builder = TextPlusMediaBuilder()
text_plus_builder.text = "hello world"

# 创建页面item
item_builder = ItemBuilder()
item_builder.add_media_builder(text_plus_builder)

# 创建播放表
play_builder = PlayBuilder()
play_builder.add_item_builder(item_builder)

# 生成播放表内容
content = play_builder.set_play_id(1).build().create_msg()

# 发送播放表
with NovaClient("localhost") as client:
    client.set_play_list(content)

# 发送查询设备点阵大小
cli = NovaClient("localhost")
cli.make_connection()
cli.get_device_size()
cli.close_connection()
```
# 其他
## 打包
```bash
python setup.py sdist bdist_wheel
```
## 本地安装
```bash
pip install highway_sdk -i http://127.0.0.1:8080/pypi/simple/ --trusted-host 127.0.0.1
```
## 在线安装
pip install highway_sdk
