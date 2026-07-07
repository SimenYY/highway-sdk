"""电明厂商设备模块。"""

from datetime import datetime

from highway_sdk.core.device import BaseDevice

from ..tags import CmsPlayItem, CmsTags
from .codec import DianMingCodec
from .spec import ENCODING, Frame, What


class DianMingDevice(BaseDevice[DianMingCodec]):
    """电明CMS设备客户端。

    所有方法成功返回业务数据（dict），失败抛 ``DeviceOperationError`` 等
    ``HighwaySDKError`` 子类异常，由调用方捕获处理。
    """

    codec = DianMingCodec

    async def _request(self, frame: Frame, timeout: float | None = None) -> Frame:
        """发送请求帧并返回解析后的响应帧。"""
        response = await self.request(frame, timeout)
        return Frame.from_bytes(response)

    # ------------------------------------------------------------------
    # 数据采集 API（返回 CmsTags.model_dump()，失败抛异常）
    # ------------------------------------------------------------------

    async def get_brightness(self) -> dict:
        """获取亮度百分比和亮度控制模式。

        Returns:
            dict: ``CmsTags.model_dump()``，仅填充 brightness、brightness_mode、timestamp。

        Raises:
            DeviceOperationError: 设备返回错误响应。
            ResponseTimeoutError: 响应超时。
            DeviceConnectionError: 连接异常。
        """
        frame = Frame(what=What.GET_BRIGHTNESS_AND_MODE_REQ)
        response = await self._request(frame)
        data = self.codec.decode(response)
        cms_tags = CmsTags(
            brightness=data["brightness"],
            brightness_mode=data["mode"],
            timestamp=datetime.now(),
        )
        return cms_tags.model_dump()

    async def get_play_item(self) -> dict:
        """获取当前播放项（结构化 + 原始格式）。

        Returns:
            dict: ``CmsTags.model_dump()``，填充 play_item（含 index）、orig_play_item、timestamp。

        Raises:
            DeviceOperationError: 设备返回错误响应。
            ResponseTimeoutError: 响应超时。
            DeviceConnectionError: 连接异常。
        """
        frame = Frame(what=What.GET_PLAY_ITEM_REQ)
        response = await self._request(frame)
        data = self.codec.decode(response)

        orig_play_item = data.get("media") or ""
        play_item = self._dict_to_cms_play_item(data)

        cms_tags = CmsTags(
            orig_play_item=orig_play_item,
            play_item=play_item,
            timestamp=datetime.now(),
        )
        return cms_tags.model_dump()

    async def get_play_list(self, play_id: int = 0, filename: str = "play00.lst") -> dict:
        """获取当前播放列表（结构化 + 原始格式）。

        Args:
            play_id: 播放列表 ID，默认为 0。
            filename: 播放列表文件名，默认为 "play00.lst"。

        Returns:
            dict: ``CmsTags.model_dump()``，填充 play_list、orig_play_list、timestamp。

        Raises:
            DeviceOperationError: 设备返回错误响应。
            ResponseTimeoutError: 响应超时。
            DeviceConnectionError: 连接异常。
        """
        offset = f"{play_id:08d}".encode("ascii")
        data = offset + filename.encode("ascii")
        frame = Frame(what=What.GET_PLAY_LIST_REQ, data=data)
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
        return cms_tags.model_dump()

    # ------------------------------------------------------------------
    # 控制类 API（成功返回 None，失败抛异常）
    # ------------------------------------------------------------------

    async def set_brightness(self, brightness: int | None = None) -> None:
        """设置亮度或控制亮度模式。

        Args:
            brightness: 亮度值(0-31)，None表示自动调节亮度模式。

        Raises:
            DeviceOperationError: 设备返回错误响应。
            ResponseTimeoutError: 响应超时。
            DeviceConnectionError: 连接异常。
        """
        if brightness is None:
            data = b"FFFFFF"
        else:
            brightness = max(0, min(31, brightness))
            data = (f"{brightness:02d}" * 3).encode("ascii")
        frame = Frame(what=What.SET_BRIGHTNESS_OR_MODE_REQ, data=data)
        response = await self._request(frame)
        self.codec.decode(response)

    async def set_play_list(self, content: str, play_id: int = 0) -> None:
        """下发播放列表并立即播放。

        DianMing 使用 SET_PLAY_LIST_AND_PLAY_REQ 单指令完成下发并播放。

        Args:
            content: 播放列表内容（可由 Play 模型生成）。
            play_id: 播放列表 ID，默认为 0（内部映射为 ``play{play_id:02d}.lst``）。

        Raises:
            DeviceOperationError: 设备返回错误响应。
            ResponseTimeoutError: 响应超时。
            DeviceConnectionError: 连接异常。
        """
        file_name = f"play{play_id:02d}.lst"
        data = b"+00000000" + file_name.encode(ENCODING) + content.encode(ENCODING)
        frame = Frame(what=What.SET_PLAY_LIST_AND_PLAY_REQ, data=data)
        response = await self._request(frame)
        self.codec.decode(response)

    # ------------------------------------------------------------------
    # 内部工具方法
    # ------------------------------------------------------------------

    @staticmethod
    def _dict_to_cms_play_item(item: dict) -> CmsPlayItem:
        """将厂商解析结果转换为统一 CmsPlayItem。"""
        index = None
        if item.get("index") and item["index"].isdigit():
            index = int(item["index"])

        text = None
        font = None
        font_color = None
        font_size = None
        image_name = None

        for media in item.get("media_list", []):
            if media.get("text") and text is None:
                text = media["text"]
            if media.get("font") and font is None:
                font = media["font"]
            if media.get("font_color") and font_color is None:
                font_color = media["font_color"]
            if media.get("font_size") and font_size is None:
                font_size = media["font_size"]
            if media.get("bmp") and image_name is None:
                image_name = media["bmp"]
            elif media.get("jpg") and image_name is None:
                image_name = media["jpg"]
            elif media.get("png") and image_name is None:
                image_name = media["png"]
            elif media.get("gif") and image_name is None:
                image_name = media["gif"]

        duration = None
        if item.get("duration") is not None:
            duration = item["duration"] // 10  # 十分之一秒 → 秒

        return CmsPlayItem(
            index=index,
            text=text,
            font=font,
            font_color=font_color,
            font_size=font_size,
            image_name=image_name,
            duration=duration,
        )
