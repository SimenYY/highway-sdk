"""显科厂商设备模块。"""

from datetime import datetime

from highway_sdk.core.device import BaseDevice
from highway_sdk.core.exceptions import HighwaySDKError
from highway_sdk.core.response import Response

from ..tags import CmsPlayItem, CmsTags
from .codec import XianKeCodec
from .spec import ENCODING, Frame, What


class XianKeDevice(BaseDevice):
    """显科CMS设备客户端。"""

    codec = XianKeCodec

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
            frame = Frame(what=What.GET_BRIGHTNESS_AND_MODE)
            response = await self._request(frame)
            data = self.codec.decode(response)
            cms_tags = CmsTags(
                brightness=data["brightness"],
                brightness_mode="manual" if data["mode"] == 1 else "auto",
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
            data = self.codec.decode(response)

            orig_play_item = data.get("text") or ""
            play_item = CmsPlayItem(
                index=0,
                text=data.get("text"),
                font=None,
                font_color=None,
                font_size=None,
                image_name=None,
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
            frame = Frame(what=What.DOWNLOAD_FILE)
            response = await self._request(frame)
            play_data = self.codec.decode(response)

            play_list = []
            orig_play_list_parts = []
            for window in play_data.get("windows", []):
                for item in window.get("items", []):
                    play_list.append(self._dict_to_cms_play_item(item))
                    orig_play_list_parts.append(item.get("media") or "")

            cms_tags = CmsTags(
                orig_play_list="\r\n".join(orig_play_list_parts),
                play_list=play_list,
                timestamp=datetime.now(),
            )
            return Response.success(data=cms_tags.model_dump())
        except HighwaySDKError as e:
            return Response.error(str(e))

    # ------------------------------------------------------------------
    # 控制类 API（保留原有接口）
    # ------------------------------------------------------------------

    async def upload_file(self, content: str, file_name: str = "list\\000.xkl") -> Response:
        """上传文件。

        Args:
            content: 文件内容。
            file_name: 文件名，默认为 "list\\000.xkl"。

        Returns:
            Response: 操作结果。
        """
        try:
            data = b"10"
            data += str(len(file_name)).encode("ascii").rjust(3, b"0")
            data += file_name.encode(ENCODING)
            data += b"0000"
            data += content.encode(ENCODING)
            frame = Frame(what=What.UPLOAD_FILE, data=data)
            response = await self._request(frame)
            self.codec.decode(response)
            return Response.success()
        except HighwaySDKError as e:
            return Response.error(str(e))

    async def select_play_list(self, file_name: str = "000.xkl") -> Response:
        """选择播放列表进行播放。

        Args:
            file_name: 播放列表文件名，默认为 "000.xkl"。

        Returns:
            Response: 操作结果。
        """
        try:
            data = file_name.encode(ENCODING)
            frame = Frame(what=What.SELECT_PLAY_LIST, data=data)
            response = await self._request(frame)
            self.codec.decode(response)
            return Response.success()
        except HighwaySDKError as e:
            return Response.error(str(e))

    # ------------------------------------------------------------------
    # 内部工具方法
    # ------------------------------------------------------------------

    @staticmethod
    def _dict_to_cms_play_item(item: dict) -> CmsPlayItem:
        """将厂商解析结果转换为统一 CmsPlayItem。"""
        text = item.get("text")
        font = item.get("font")
        font_color = item.get("font_color")
        font_size = item.get("font_size")

        image_name = None
        for key in ("bmp", "gif", "mpg"):
            if item.get(key):
                image_name = item[key]
                break

        duration = None
        if item.get("duration") is not None:
            duration = item["duration"]  # 显科 duration 单位已经是秒

        return CmsPlayItem(
            index=None,
            text=text,
            font=font,
            font_color=font_color,
            font_size=font_size,
            image_name=image_name,
            duration=duration,
        )
