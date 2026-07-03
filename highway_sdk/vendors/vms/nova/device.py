"""诺瓦厂商设备模块。"""

import struct
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
from .codec import NovaCodec
from .spec import ENCODING, Frame, What


class NovaDevice(BaseDevice):
    """诺瓦VMS设备客户端。"""

    codec = NovaCodec

    async def _request(self, frame: Frame, timeout: float = 3.0) -> Frame:
        """发送请求帧并返回解析后的响应帧。"""
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
            frame = Frame(what=What.GET_BRIGHTNESS_REQ)
            response = await self._request(frame)
            tags: BrightnessTags = self.codec.decode(response)
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
            frame = Frame(what=What.GET_PLAY_ITEM_REQ)
            response = await self._request(frame)
            item_tags: ItemTags = self.codec.decode(response)

            orig_play_item = item_tags.text or ""
            play_item = CmsPlayItem(
                index=0,  # 诺瓦单条播放，默认 index=0
                text=item_tags.text,
                font=None,
                font_color=None,
                font_size=None,
                image_name=item_tags.image_name,
                duration=None,
            )

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
            frame = Frame(what=What.GET_PLAY_LIST_REQ)
            response = await self._request(frame)
            play_tags: PlayTags = self.codec.decode(response)

            play_list = [
                self._item_tags_to_cms_play_item(item) for window in play_tags.windows for item in window.items
            ]
            orig_play_list = "\r\n".join(
                item.media or item.text or "" for window in play_tags.windows for item in window.items
            )

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

    async def send_file_name(self, file_name: str = "play001.lst", block_size: int = 65535) -> Response:
        """发送文件名。

        Args:
            file_name: 文件名，默认为 "play001.lst"。
            block_size: 块大小，默认为 65535。

        Returns:
            Response: 操作结果。
        """
        try:
            data = struct.pack("<H", block_size) + file_name.encode(ENCODING)
            frame = Frame(what=What.SEND_FILE_NAME_REQ, data=data)
            response = await self._request(frame)
            self.codec.decode(response)
            return Response.success()
        except HighwaySDKError as e:
            return Response.error(str(e))

    async def send_file_content(self, content: str, block_num: int = 1) -> Response:
        """发送文件内容。

        Args:
            content: 文件内容。
            block_num: 块号，默认为 1。

        Returns:
            Response: 操作结果。
        """
        try:
            data = struct.pack("<H", block_num) + content.encode(ENCODING)
            frame = Frame(what=What.SEND_FILE_CONTENT_REQ, data=data)
            response = await self._request(frame)
            self.codec.decode(response)
            return Response.success()
        except HighwaySDKError as e:
            return Response.error(str(e))

    async def select_play_list(self, playlist_id: int = 1) -> Response:
        """指定播放列表进行播放。

        Args:
            playlist_id: 播放列表 ID，默认为 1。

        Returns:
            Response: 操作结果。
        """
        try:
            data = struct.pack(">B", playlist_id)
            frame = Frame(what=What.SELECT_PLAY_LIST_REQ, data=data)
            response = await self._request(frame)
            self.codec.decode(response)
            return Response.success()
        except HighwaySDKError as e:
            return Response.error(str(e))

    # ------------------------------------------------------------------
    # 内部工具方法
    # ------------------------------------------------------------------

    @staticmethod
    def _item_tags_to_cms_play_item(item: ItemTags) -> CmsPlayItem:
        """将厂商原生 ItemTags 转换为统一 CmsPlayItem。"""
        text = item.text
        font = None
        font_color = None
        font_size = None
        image_name = item.image_name

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
            duration = item.duration // 10  # 十分之一秒 → 秒

        return CmsPlayItem(
            index=None,
            text=text,
            font=font,
            font_color=font_color,
            font_size=font_size,
            image_name=image_name,
            duration=duration,
        )
