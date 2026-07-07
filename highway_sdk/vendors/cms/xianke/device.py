"""显科厂商设备模块。"""

from datetime import datetime

from highway_sdk.core.device import BaseDevice

from ..tags import CmsPlayItem, CmsTags
from .codec import XianKeCodec
from .spec import ENCODING, Frame, What


class XianKeDevice(BaseDevice[XianKeCodec]):
    """显科CMS设备客户端。

    所有方法成功返回业务数据（dict）或 None，失败抛 ``DeviceOperationError`` 等
    ``HighwaySDKError`` 子类异常，由调用方捕获处理。
    """

    codec = XianKeCodec

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
        frame = Frame(what=What.GET_BRIGHTNESS_AND_MODE)
        response = await self._request(frame)
        data = self.codec.decode(response)
        cms_tags = CmsTags(
            brightness=data["brightness"],
            brightness_mode="manual" if data["mode"] == 1 else "auto",
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
        return cms_tags.model_dump()

    async def get_play_list(self, play_id: int = 0) -> dict:
        """获取当前播放列表（结构化 + 原始格式）。

        Args:
            play_id: 播放列表 ID，默认为 0。

        Returns:
            dict: ``CmsTags.model_dump()``，填充 play_list、orig_play_list、timestamp。

        Raises:
            DeviceOperationError: 设备返回错误响应。
            ResponseTimeoutError: 响应超时。
            DeviceConnectionError: 连接异常。
        """
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
        return cms_tags.model_dump()

    # ------------------------------------------------------------------
    # 控制类 API（成功返回 None，失败抛异常）
    # ------------------------------------------------------------------

    async def upload_file(self, content: str, file_name: str = "list\\000.xkl") -> None:
        """上传文件。

        Args:
            content: 文件内容。
            file_name: 文件名，默认为 "list\\000.xkl"。

        Raises:
            DeviceOperationError: 设备返回错误响应。
            ResponseTimeoutError: 响应超时。
            DeviceConnectionError: 连接异常。
        """
        data = b"10"
        data += str(len(file_name)).encode("ascii").rjust(3, b"0")
        data += file_name.encode(ENCODING)
        data += b"0000"
        data += content.encode(ENCODING)
        frame = Frame(what=What.UPLOAD_FILE, data=data)
        response = await self._request(frame)
        self.codec.decode(response)

    async def select_play_list(self, file_name: str = "000.xkl") -> None:
        """选择播放列表进行播放。

        Args:
            file_name: 播放列表文件名，默认为 "000.xkl"。

        Raises:
            DeviceOperationError: 设备返回错误响应。
            ResponseTimeoutError: 响应超时。
            DeviceConnectionError: 连接异常。
        """
        data = file_name.encode(ENCODING)
        frame = Frame(what=What.SELECT_PLAY_LIST, data=data)
        response = await self._request(frame)
        self.codec.decode(response)

    async def set_play_list(self, content: str, file_name: str = "list\\000.xkl") -> None:
        """下发播放列表并立即播放。

        XianKe 需要两步：upload_file 上传文件 → select_play_list 触发播放。
        任一步失败抛异常，后续步骤不执行。

        Args:
            content: 播放列表内容字符串（由 Play 模型生成）。
            file_name: 文件名，默认为 ``list\\000.xkl``（XianKe 协议规定的特殊命名，
                含 ``\\`` 路径分隔符；select 时取 basename ``000.xkl``）。

        Raises:
            DeviceOperationError: 设备返回错误响应。
            ResponseTimeoutError: 响应超时。
            DeviceConnectionError: 连接异常。
        """
        await self.upload_file(content, file_name)
        play_name = file_name.split("\\")[-1] if "\\" in file_name else file_name
        await self.select_play_list(play_name)

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
