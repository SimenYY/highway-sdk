import itertools
import logging
from datetime import datetime
from typing import Protocol

import aiomqtt

from highway_sdk.core.base import BaseTags
from highway_sdk.vendors.vms._common import VmsTextBuilder
from highway_sdk.vendors.vms.fenghai.media import (
    Bmp as FenghaiBmp,
    Color as FenghaiColor,
    Font as FenghaiFont,
    FontSize as FenghaiFontSize,
    Item as FenghaiItem,
    Play as FenghaiPlay,
    Text as FenghaiText,
)
from highway_sdk.vendors.vms.fenghai.protocol import VmsFenghaiProtocol

from .models import DeviceInfoMode, RealtimeDataPublishModel
from .tags import (
    ControlVmsTagsModel,
    _ColorEnum,
    _FontEnum,
    convert,
)

__all__ = [
    "MQTTGatewayProtocol",
    "SupaiotVmsFenghaiProtocol",
]

logger = logging.getLogger(__name__)


class MQTTGatewayProtocol(Protocol):
    """用于接入物联智控MQTT网关的协议"""

    def mqtt_real_publish(self, series: str, sn: str, data: dict):
        """发送实时数据"""
        ...


# ==============================================================================
# 情报板
# ==============================================================================
class SupaiotVmsFenghaiProtocol(VmsFenghaiProtocol):
    """物联智控 情报板 丰海协议"""

    def __init__(self, *, device_info: DeviceInfoMode, mqtt_client: aiomqtt.Client, **kwargs):
        super().__init__(**kwargs)

        self.device_info = device_info
        self.mqtt_client = mqtt_client

    def on_message_parsed(self, tags: BaseTags):
        try:
            data = convert(tags)
            if data:
                self.mqtt_real_publish(self.device_info.series, self.device_info.sn, data)
        except Exception as e:
            self.log.exception(e)

    def on_connected(self) -> None:
        # 设置设备状态轮询
        self.add_interval_job(self.download_file, 2.0, jitter=2)
        self.add_interval_job(self.get_play_item, 2.0, jitter=2)

    def mqtt_real_publish(self, series: str, sn: str, data: dict):
        # self.mqtt_client.publish_real_data(series, sn, data)
        prmm = RealtimeDataPublishModel(series=series, sn=sn, time=datetime.now(), timestamp=None, data=data)
        self._loop.create_task(
            self.mqtt_client.publish(topic=prmm.get_topic(), payload=prmm.model_dump_json(exclude_none=True))
        )

    def play_speed_limit(self, speed_limit: int):
        media = FenghaiBmp(bmp_file_name=f"{speed_limit:03d}")
        item = FenghaiItem(media_list=[media], duration=30000)
        play = FenghaiPlay(item_list=[item])
        self.upload_file(str(play))

    def control(self, control_tags: ControlVmsTagsModel):
        tags = control_tags.model_dump(exclude_none=True)
        play = FenghaiPlay()
        if "KZCT" in tags:  # 兼容限速标，以图片发送
            media = FenghaiBmp(bmp_file_name=f"{int(tags['KZCT'])}")
            item = FenghaiItem(media_list=[media], duration=30000)
            play.item_list.append(item)
        else:
            for i in itertools.count(1):
                content = tags.get(f"KZCT{i}")

                if content is None:
                    break
                content = str(content).replace("\\n", "")  # 去掉下发的换行符
                if str(content).isdigit():
                    media = FenghaiBmp(bmp_file_name=f"{int(content)}:03d")
                else:
                    # 自动调整文本
                    vms_text = VmsTextBuilder(
                        text=content,
                        h=self.device_info.extra["h"],
                        w=self.device_info.extra["w"],
                        max_size=FenghaiFontSize._64.value,
                        min_size=FenghaiFontSize._16.value,
                        size_range=[size.value for size in FenghaiFontSize],
                        lf="\\n",
                    ).build()

                    font_code = tags.get(f"KFO{i}", "102")
                    font_color_code = tags.get(f"KFC{i}", "1")
                    media = FenghaiText(
                        x=vms_text.xy[0],
                        y=vms_text.xy[1],
                        text=vms_text.text,
                        font_color=FenghaiColor(_ColorEnum.get_rgba_by_code(int(font_color_code))),
                        font=FenghaiFont(_FontEnum.get_font_by_code(int(font_code))),
                        font_size=FenghaiFontSize(value=vms_text.size),
                    )
                duration = int(tags.get(f"KTI{i}", "10"))
                item = FenghaiItem(media_list=[media], duration=duration * 100)
                play.item_list.append(item)
        self.upload_file(str(play))
