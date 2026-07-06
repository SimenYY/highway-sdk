"""诺瓦厂商设备模块。"""

import struct
from datetime import datetime

from highway_sdk.core.device import BaseDevice
from highway_sdk.core.exceptions import HighwaySDKError
from highway_sdk.core.response import Response

from ..tags import CmsPlayItem, CmsTags
from .codec import NovaCodec
from .spec import ENCODING, Frame, What


class NovaDevice(BaseDevice[NovaCodec]):
    """诺瓦CMS设备客户端。"""

    codec = NovaCodec

    async def _request(self, frame: Frame, timeout: float | None = None) -> Frame:
        """发送请求帧并返回解析后的响应帧。"""
        response = await self.request(frame, timeout)
        return Frame.from_bytes(response)

    # ------------------------------------------------------------------
    # 数据采集 API（统一返回 Response + CmsTags）
    # ------------------------------------------------------------------

    async def get_brightness(self) -> Response:
        """获取亮度百分比和亮度控制模式。

        通过查询设备状态（0x01/0x02）获取亮度信息。

        Returns:
            Response: data 为 CmsTags，仅填充 brightness、brightness_mode、timestamp。

        注：
            亮度级别 1-255 按 round(level * 100 / 255) 折算为百分比 0-100；
            亮度控制方式 1-自动 / 2-手动 / 3-定时。
        """
        try:
            frame = Frame(what=What.GET_DEVICE_STATUS_REQ)
            response = await self._request(frame)
            data = self.codec.decode(response)
            # 1-auto / 2-manual / 3-timed
            mode_map = {1: "auto", 2: "manual", 3: "timed"}
            brightness_pct = round(data["brightness_level"] * 100 / 255)
            cms_tags = CmsTags(
                brightness=brightness_pct,
                brightness_mode=mode_map[data["mode"]],
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
            data = self.codec.decode(response)

            orig_play_item = data.get("text") or ""
            play_item = CmsPlayItem(
                index=0,  # 诺瓦单条播放，默认 index=0
                text=data.get("text"),
                font=None,
                font_color=None,
                font_size=None,
                image_name=data.get("image_name"),
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
        """获取当前播放列表（原始格式）。

        Nova 0x3B 响应内容为类 INI 文本（见协议附录一），结构复杂，
        本方法仅保留原始文本字符串，不做结构化解析。

        Args:
            play_id: 播放列表 ID，默认为 0（仅用于接口兼容，实际使用设备返回的 list_no）。

        Returns:
            Response: data 为 CmsTags，填充 orig_play_list、timestamp；
            play_list 为空列表（结构化解析未实现）。
        """
        try:
            frame = Frame(what=What.GET_PLAY_LIST_REQ)
            response = await self._request(frame)
            data = self.codec.decode(response)

            orig_play_list = data.get("text") or ""
            cms_tags = CmsTags(
                orig_play_list=orig_play_list,
                play_list=[],
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

    async def set_play_list(self, content: str, file_name: str = "play001.lst") -> Response:
        """下发播放列表并立即播放。

        Nova 需要三步：发送文件名 → 发送文件内容 → 选择播放列表。

        Args:
            content: 播放列表内容字符串。
            file_name: 文件名，默认为 "play001.lst"。

        Returns:
            Response: 操作结果。
        """
        resp = await self.send_file_name(file_name)
        if resp.status != "success":
            return resp
        resp = await self.send_file_content(content)
        if resp.status != "success":
            return resp
        return await self.select_play_list(1)
