"""三思厂商设备模块。"""

from datetime import datetime

from highway_sdk.core.device import BaseDevice
from highway_sdk.core.exceptions import HighwaySDKError
from highway_sdk.core.response import Response

from ..tags import (
    BrightnessMode,
    BrightnessTags,
    CmsPlayItem,
    CmsTags,
    ItemTags,
    PlayTags,
)
from .codec import SanSiCodec
from .spec import ENCODING, Frame, What


class SanSiDevice(BaseDevice):
    """三思VMS设备客户端。"""

    codec = SanSiCodec

    async def _request(self, frame: Frame, timeout: float = 3.0) -> Frame:
        """发送请求帧并返回解析后的响应帧（SanSi 响应无 what 字段）。"""
        response = await self.request(frame, timeout)
        return Frame.from_bytes(response)

    # ------------------------------------------------------------------
    # 数据采集 API（统一返回 Response + CmsTags）
    # ------------------------------------------------------------------

    async def get_brightness(self) -> Response:
        """获取亮度百分比和亮度控制模式。

        Returns:
            Response: data 为 CmsTags，仅填充 brightness、brightness_mode、timestamp。
        """
        try:
            frame = Frame(what=What.GET_BRIGHTNESS_AND_MODE)
            response = await self._request(frame)
            tags: BrightnessTags = self.codec.decode_get_brightness(response.data)
            cms_tags = CmsTags(
                brightness=tags.brightness,
                brightness_mode="auto" if tags.mode == BrightnessMode.AUTO else "manual",
                timestamp=datetime.now(),
            )
            return Response.success(data=cms_tags.model_dump())
        except HighwaySDKError as e:
            return Response.error(str(e))

    async def get_play_item(self) -> Response:
        """获取当前播放项（结构化 + 原始格式）。

        Returns:
            Response: data 为 CmsTags，填充 play_item（含 index）、orig_play_item、timestamp。
        """
        try:
            frame = Frame(what=What.GET_PLAY_ITEM)
            response = await self._request(frame)
            item_tags: ItemTags = self.codec.decode_get_play_item(response.data)

            orig_play_item = item_tags.media or ""
            play_item = self._item_tags_to_cms_play_item(item_tags)

            cms_tags = CmsTags(
                orig_play_item=orig_play_item,
                play_item=play_item,
                timestamp=datetime.now(),
            )
            return Response.success(data=cms_tags.model_dump())
        except HighwaySDKError as e:
            return Response.error(str(e))

    async def get_play_list(self, play_id: int = 0) -> Response:
        """获取当前播放列表（结构化 + 原始格式）。

        Args:
            play_id: 播放列表 ID，默认为 0。

        Returns:
            Response: data 为 CmsTags，填充 play_list、orig_play_list、timestamp。
        """
        try:
            frame = Frame(what=What.DOWNLOAD_FILE)
            response = await self._request(frame)
            play_tags: PlayTags = self.codec.decode_download_file(response.data)

            play_list = [
                self._item_tags_to_cms_play_item(item) for window in play_tags.windows for item in window.items
            ]
            orig_play_list = "\r\n".join(item.media or "" for window in play_tags.windows for item in window.items)

            cms_tags = CmsTags(
                orig_play_list=orig_play_list,
                play_list=play_list,
                timestamp=datetime.now(),
            )
            return Response.success(data=cms_tags.model_dump())
        except HighwaySDKError as e:
            return Response.error(str(e))

    # ------------------------------------------------------------------
    # 控制类 API（保留原有接口）
    # ------------------------------------------------------------------

    async def set_brightness(self, brightness: int) -> Response:
        """设置亮度。

        Args:
            brightness: 亮度值，范围0-31。

        Returns:
            Response: 操作结果。
        """
        try:
            brightness = max(0, min(31, brightness))
            data = (f"{brightness:02d}".encode("ascii")) * 3
            frame = Frame(what=What.SET_BRIGHTNESS, data=data)
            response = await self._request(frame)
            self.codec.decode_set_brightness(response.data)
            return Response.success()
        except HighwaySDKError as e:
            return Response.error(str(e))

    async def upload_file(self, content: str, file_name: str = "play.lst") -> Response:
        """上传播放列表文件。

        Args:
            content: 文件内容。
            file_name: 文件名，默认为 "play.lst"。

        Returns:
            Response: 操作结果。
        """
        try:
            data = file_name.encode(ENCODING) + b"+" + b"\x00\x00\x00\x00" + content.encode(ENCODING)
            frame = Frame(what=What.UPLOAD_FILE, data=data)
            response = await self._request(frame)
            self.codec.decode_upload_file(response.data)
            return Response.success()
        except HighwaySDKError as e:
            return Response.error(str(e))

    # ------------------------------------------------------------------
    # 内部工具方法
    # ------------------------------------------------------------------

    @staticmethod
    def _item_tags_to_cms_play_item(item: ItemTags) -> CmsPlayItem:
        """将厂商原生 ItemTags 转换为统一 CmsPlayItem。"""
        index = None
        if item.index and item.index.isdigit():
            index = int(item.index)

        text = item.text
        font = item.font
        font_color = item.font_color
        font_size = item.font_size
        image_name = None

        for media in item.media_list:
            if media.text and text is None:
                text = media.text
            if media.font and font is None:
                font = media.font
            if media.font_color and font_color is None:
                font_color = media.font_color
            if media.font_size and font_size is None:
                font_size = media.font_size
            if media.bmp and image_name is None:
                image_name = media.bmp
            elif media.jpg and image_name is None:
                image_name = media.jpg
            elif media.png and image_name is None:
                image_name = media.png
            elif media.gif and image_name is None:
                image_name = media.gif

        duration = None
        if item.duration is not None:
            duration = item.duration  # 三思已经转换为秒

        return CmsPlayItem(
            index=index,
            text=text,
            font=font,
            font_color=font_color,
            font_size=font_size,
            image_name=image_name,
            duration=duration,
        )
