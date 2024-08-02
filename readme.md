# supcon_highway_sdk
# 介绍
本项目主要作用是作为公路交通领域，机电设备、智能设备等设备协议SDK封装，方便开发者统一用Python快速建立起对设备的交互
# SDK使用说明
## VMS 情报板
### Nova
#### 节目播放功能
###### 文本媒体播放
```python
# 创建一个nova客户端
cli = NovaClient('127.0.0.1')
# 创建一个节目构造器
play_br = PlayBuilder()
# 创建节目页面构造器
item_br = ItemBuilder()
# 创建文本媒体构造器
text_br = TextMediaBuilder()
# 添加媒体参数
text_br.x = 10
text_br.y = 10
text_br.width = 200
text_br.height = 100
text_br.text = 'Hello World'
text_br.text_color = '1'
text_br.background_color = '8'

# 给页面添加媒体
item_br.add_media_builder(text_br)

# 设置节目编号, 并添加页面
play_br.set_play_id(1).add_item_builder(item_br)

# 创建播放管理器
pm = PlayManager(play_builder=play_br, nova_traffic=cli)

# 一键播放
pm.play()
```
###### web页面播放
待补充

# 其他
## 打包
```bash
python setup.py sdist bdist_wheel
```
