"""诺瓦厂商设备模块。"""

import struct
from datetime import datetime
from typing import ClassVar

from highway_sdk.core.device import BaseDevice

from ..tags import CmsPlayItem, CmsTags
from .codec import NovaCodec
from .spec import ENCODING, Frame, What


class NovaCms(BaseDevice[NovaCodec]):
    """诺瓦CMS设备客户端。

    所有方法成功返回业务数据（CmsTags）或 None，失败抛 ``DeviceOperationError`` 等
    ``HighwaySDKError`` 子类异常，由调用方捕获处理。
    """

    codec = NovaCodec

    async def _request(self, frame: Frame, timeout: float | None = None) -> Frame:
        """发送请求帧并返回解析后的响应帧。"""
        response = await self.request(frame, timeout)
        return Frame.from_bytes(response)

    # ------------------------------------------------------------------
    # 数据采集 API（返回 CmsTags，失败抛异常）
    # ------------------------------------------------------------------

    async def get_brightness(self) -> CmsTags:
        """获取亮度百分比和亮度控制模式。

        通过查询设备状态（0x01/0x02）获取亮度信息。

        Returns:
            CmsTags: 仅填充 brightness、brightness_mode、timestamp。

        Raises:
            DeviceOperationError: 设备返回错误响应。
            ResponseTimeoutError: 响应超时。
            DeviceConnectionError: 连接异常。

        注：
            亮度级别 1-255 按 round(level * 100 / 255) 折算为百分比 0-100；
            亮度控制方式 1-自动 / 2-手动 / 3-定时。
        """
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
        return cms_tags

    async def get_play_item(self) -> CmsTags:
        """获取当前播放项（结构化 + 原始格式）。

        Returns:
            CmsTags: 填充 play_item（含 index）、orig_play_item、timestamp。

        Raises:
            DeviceOperationError: 设备返回错误响应。
            ResponseTimeoutError: 响应超时。
            DeviceConnectionError: 连接异常。
        """
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
        return cms_tags

    async def get_play_list(self, play_id: int = 0) -> CmsTags:
        """获取当前播放列表（原始格式）。

        Nova 0x3B 响应内容为类 INI 文本（见协议附录一），结构复杂，
        本方法仅保留原始文本字符串，不做结构化解析。

        Args:
            play_id: 播放列表 ID，默认为 0（仅用于接口兼容，实际使用设备返回的 list_no）。

        Returns:
            CmsTags: 填充 orig_play_list、timestamp；
            play_list 为空列表（结构化解析未实现）。

        Raises:
            DeviceOperationError: 设备返回错误响应。
            ResponseTimeoutError: 响应超时。
            DeviceConnectionError: 连接异常。
        """
        frame = Frame(what=What.GET_PLAY_LIST_REQ)
        response = await self._request(frame)
        data = self.codec.decode(response)

        orig_play_list = data.get("text") or ""
        cms_tags = CmsTags(
            orig_play_list=orig_play_list,
            play_list=[],
            timestamp=datetime.now(),
        )
        return cms_tags

    async def get_screen_size(self) -> tuple[int, int]:
        """获取屏幕分辨率（宽, 高）。

        用于配合 ``TextLayout`` 工具计算文字居中布局：先查询屏幕尺寸，
        再据此计算适配字号和居中坐标。

        Returns:
            tuple[int, int]: ``(width, height)`` 像素。

        Raises:
            DeviceOperationError: 设备返回错误响应。
            ResponseTimeoutError: 响应超时。
            DeviceConnectionError: 连接异常。
        """
        frame = Frame(what=What.GET_SCREEN_SIZE_REQ)
        response = await self._request(frame)
        data = self.codec.decode(response)
        return data["width"], data["height"]

    # ------------------------------------------------------------------
    # 控制类 API（成功返回 None，失败抛异常）
    # ------------------------------------------------------------------

    async def send_file_name(self, file_name: str = "play001.lst", block_size: int = 65535) -> None:
        """发送文件名。

        Args:
            file_name: 文件名，默认为 "play001.lst"。
            block_size: 块大小，默认为 65535。

        Raises:
            DeviceOperationError: 设备返回错误响应。
            ResponseTimeoutError: 响应超时。
            DeviceConnectionError: 连接异常。
        """
        data = struct.pack("<H", block_size) + file_name.encode(ENCODING)
        frame = Frame(what=What.SEND_FILE_NAME_REQ, data=data)
        response = await self._request(frame)
        self.codec.decode(response)

    async def send_file_content(self, content: str, block_num: int = 1) -> None:
        """发送文件内容。

        Args:
            content: 文件内容。
            block_num: 块号，默认为 1。

        Raises:
            DeviceOperationError: 设备返回错误响应。
            ResponseTimeoutError: 响应超时。
            DeviceConnectionError: 连接异常。
        """
        data = struct.pack("<H", block_num) + content.encode(ENCODING)
        frame = Frame(what=What.SEND_FILE_CONTENT_REQ, data=data)
        response = await self._request(frame)
        self.codec.decode(response)

    async def select_play_list(self, playlist_id: int = 1) -> None:
        """指定播放列表进行播放。

        Args:
            playlist_id: 播放列表 ID，默认为 1。

        Raises:
            DeviceOperationError: 设备返回错误响应。
            ResponseTimeoutError: 响应超时。
            DeviceConnectionError: 连接异常。
        """
        data = struct.pack(">B", playlist_id)
        frame = Frame(what=What.SELECT_PLAY_LIST_REQ, data=data)
        response = await self._request(frame)
        self.codec.decode(response)

    async def set_play_list(self, items: list[CmsPlayItem], file_name: str = "play001.lst") -> None:
        """下发播放列表并立即播放。

        Nova 需要三步：发送文件名 → 发送文件内容 → 选择播放列表。
        任一步失败即抛异常，后续步骤不再执行。

        Args:
            items: 播放项列表。
            file_name: 文件名，默认为 "play001.lst"。

        Raises:
            DeviceOperationError: 设备返回错误响应。
            ResponseTimeoutError: 响应超时。
            DeviceConnectionError: 连接异常。
        """
        content = self._items_to_content(items)
        await self.send_file_name(file_name)
        await self.send_file_content(content)
        await self.select_play_list(1)

    # ------------------------------------------------------------------
    # 内部工具方法
    # ------------------------------------------------------------------

    # 中文字体名 → 单字符字体代码（与 DianMing 协议一致）
    _FONT_NAME_MAP: ClassVar[dict[str, str]] = {
        "黑体": "h",
        "楷体": "k",
        "宋体": "s",
        "仿宋": "f",
    }

    @staticmethod
    def _hex_color_to_vendor(hex_color: str | None) -> str:
        """将 '#RRGGBB' 转换为厂商颜色字符串（'RRRGGGBBB000'）。"""
        if hex_color is None:
            return "000000000000"
        hex_color = hex_color.lstrip("#")
        if len(hex_color) != 6:
            return "000000000000"
        try:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
        except ValueError:
            return "000000000000"
        return f"{r:03d}{g:03d}{b:03d}000"

    @staticmethod
    def _font_size_code(font_size: int | None) -> str:
        """将字号转换为协议要求的重复格式（如 24 → '2424'），默认 32。"""
        size = font_size if font_size is not None else 32
        if size < 0:
            size = 32
        return f"{size}{size}"

    @classmethod
    def _item_to_str(cls, item: CmsPlayItem) -> str:
        """将单个 CmsPlayItem 转换为 INI 文本中的 item 行内容。

        优先使用 ``CmsPlayItem.x`` / ``CmsPlayItem.y`` 作为渲染坐标，缺失时默认 0。
        配合 ``TextLayout`` 工具可实现文字居中显示。
        """
        duration = item.duration if item.duration is not None else 10
        x = item.x or 0
        y = item.y or 0
        coord = f"\\C{x:03d}{y:03d}"
        # item 行格式：duration,screen_in,play_effect,screen_out,play_speed,媒体串
        # Nova 无明确字段定义，沿用 demo 中的格式（与 DianMing 一致）
        media_str_parts: list[str] = []
        if item.text is not None:
            font_code = cls._FONT_NAME_MAP.get(item.font or "黑体", "h")
            color = cls._hex_color_to_vendor(item.font_color)
            font_size_code = cls._font_size_code(item.font_size)
            media_str_parts.append(f"{coord}\\F{font_code}{font_size_code}\\T{color}\\W{item.text}")
        if item.image_name:
            # Nova 无图片媒体协议定义，沿用通用 \I 转义码占位
            media_str_parts.append(f"{coord}\\I{item.image_name.rjust(3, '0')}")
        if not media_str_parts:
            # 兜底：空文本
            media_str_parts.append(f"{coord}\\Fh3232\\T000000000000\\W")
        media_str = "".join(media_str_parts)
        return f"{duration},0,0,0,0,{media_str}"

    @classmethod
    def _items_to_content(cls, items: list[CmsPlayItem]) -> str:
        """将 CmsPlayItem 列表转换为 Nova INI 协议文本。

        Nova 没有 Play/Item 模型，直接构造 INI 文本：
            [PLAYLIST]\\r\\n
            ITEM_NO={count:03d}\\r\\n
            ITEM{index:03d}={duration},0,0,0,0,{media_str}\\r\\n

        - CmsPlayItem.duration 单位为秒，Nova 沿用秒（无需转换）
        - 缺失字段使用默认值：x=0, y=0, screen_in=0, play_effect=0, screen_out=0, play_speed=0
        """
        if not items:
            raise ValueError("播放列表不能为空")
        lines = ["[PLAYLIST]\r\n", f"ITEM_NO={len(items):03d}\r\n"]
        for i, item in enumerate(items):
            lines.append(f"ITEM{i:03d}={cls._item_to_str(item)}\r\n")
        return "".join(lines)
