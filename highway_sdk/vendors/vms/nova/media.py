import io
from abc import abstractmethod
from ftplib import CRLF
from pydantic import (
    BaseModel,
    NonNegativeInt,
    Field,
    field_validator,
    HttpUrl,
    PrivateAttr,
    ConfigDict,
)
from enum import Enum
from typing import List, Any
import configparser
import re

#TODO: 修改

# ==============================================================================
# 枚举量
# ==============================================================================
class FontEnum(str, Enum):
    HEI_TI = "1"
    KAI_TI = "2"
    SONG_TI = "3"
    FANG_SONG = "4"
    LI_SHU = "5"


class ColorEnum(str, Enum):
    RED = "1"
    GREEN = "2"
    BLUE = "3"
    YELLOW = "4"
    PURPLE = "5"  # 紫色
    CYAN = "6"  # 青色
    WHITE = "7"
    BLACK = "8"


class FontStyleEnum(str, Enum):
    NORMAL = "0"
    BOLD = "1"  # 加粗
    ITALIC = "2"  # 斜体
    UNDERLINE = "3"  # 下划线
    STRIKE = "4"  # 中划线


class AlignEnum(str, Enum):
    HORIZONTAL = "0"  # 横向
    VERTICAL = "1"  # 纵向


class HorizontalAlignmentEnum(str, Enum):
    LEFT = "0"
    RIGHT = "1"
    CENTER = "2"


class VerticalAlignmentEnum(str, Enum):
    TOP = "0"
    BOTTOM = "1"
    CENTER = "2"


class PlayEffectEnum(str, Enum):
    NONE = "0"
    NORMAL = "1"
    MOVE_UP = "2"
    MOVE_DOWN = "3"
    MOVE_LEFT = "4"
    MOVE_RIGHT = "5"


class EffectSpeedEnum(str, Enum):
    SLOWEST = "0"
    SLOWER = "1"
    NORMAL = "2"
    FASTER = "3"
    FASTEST = "4"


class IsPlayTextVoiceEnum(str, Enum):
    YES = "1"
    NO = "0"


class IsSyncPlayEnum(str, Enum):
    YES = "1"
    NO = "0"


class VoiceSoundEnum(str, Enum):
    COMMON_FEMALE_VOICE = "0"
    COMMON_MALE_VOICE = "1"
    SPECIAL_MALE_VOICE = "2"
    EMOTIONAL_MALE_VOICE = "3"
    EMOTIONAL_CHILDREN_VOICE = "4"


# ==============================================================================
# 基类
# ==============================================================================
class BaseMedia(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    _index: NonNegativeInt = PrivateAttr(
        default_factory=int
    )  # 使用 PrivateAttr() 并允许初始化
    x: NonNegativeInt  # x坐标
    y: NonNegativeInt  # y坐标
    width: NonNegativeInt  # 宽度
    height: NonNegativeInt  # 高度
    duration: NonNegativeInt  # 停留时间


class BaseMediaBuilder:
    def __init__(self):
        self._index: int = 0  # 从 1 开始
        self.x: int = 0
        self.y: int = 0
        self.width: int = 0
        self.height: int = 0
        self.duration: int = 0

    @abstractmethod
    def build(self, *args, **kwargs) -> BaseMedia:
        pass


# ==============================================================================
# 媒体类
# ==============================================================================
class _TextMedia(BaseMedia):
    font: FontEnum  # 字体
    text_size: int  # 字体大小
    text_color: ColorEnum  # 文本颜色
    background_color: ColorEnum  # 背景颜色
    text: str  # 文本
    flash: str  # 闪烁
    font_style: FontStyleEnum  # 字体样式
    world_space: int = Field(..., ge=0, le=100)  # 字体间距
    alignment_direction: int  # 排列方向

    @field_validator("text_size")
    @classmethod
    def validate_text_size(cls, value: int):
        value_str = str(value)
        length = len(value_str)
        half_len = int(length / 2)
        if length % 2 != 0:
            raise ValueError("Text size 格式不正确，e.g. 1616， 2424")
        elif value_str[:half_len] != value_str[half_len:]:
            raise ValueError("Text size 格式不正确，e.g. 1616， 2424")
        else:
            return value

    def __str__(self) -> str:
        protocol_1 = (
            f"txt{self._index}="
            f"{self.x},"
            f"{self.y},"
            f"{self.font},"
            f"{self.text_size},"
            f"{self.text_color},"
            f"{self.background_color},"
            f"{self.flash},"
            f"{self.text},"
            f"{self.width},"
            f"{self.height},"
            f"{self.font_style}"
        )

        protocol_2 = (
            f"txtparam{self._index}={self.world_space},{self.alignment_direction}"
        )

        protocol = protocol_1 + CRLF + protocol_2

        return protocol


class _TextextMedia(BaseMedia):
    """扩展文本

    Args:
        BaseMedia (_type_): _description_

    Returns:
        _type_: _description_
    """

    font: FontEnum  # 字体
    text_size: int  # 字体大小
    font_style: FontStyleEnum  # 字体样式
    horizontal_alignment: HorizontalAlignmentEnum  # 水平对齐
    vertical_alignment: VerticalAlignmentEnum  # 垂直对齐
    line_space: int = Field(..., ge=0, le=100)  # 行间距
    word_space: int = Field(..., ge=0, le=100)  # 字间距
    text_color: ColorEnum  # 文本颜色
    background_color: ColorEnum  # 背景颜色
    play_effect: PlayEffectEnum  # 播放效果
    effect_speed: EffectSpeedEnum  # 播放速度
    play_count: int = Field(..., ge=0, le=255)  # 播放次数
    text: str  # 文本
    is_play_text_voice: IsPlayTextVoiceEnum  # 是否播放文本语音
    is_sync_play: IsSyncPlayEnum  # 是否同步播放
    voice_sound: VoiceSoundEnum  # 声音
    volume: int = Field(..., ge=0, le=9)  # 音量
    voice_speed: int = Field(..., ge=0, le=9)  # 语速
    intonation: int = Field(..., ge=0, le=9)  # 音调

    def __str__(self) -> str:
        protocol = (
            f"txtext{self._index}="
            f"{self.x},"
            f"{self.y},"
            f"{self.width},"
            f"{self.height},"
            f"{self.font},"
            f"{self.text_size},"
            f"{self.font_style},"
            f"{self.horizontal_alignment},"
            f"{self.vertical_alignment},"
            f"{self.line_space},"
            f"{self.word_space},"
            f"{self.text_color},"
            f"{self.background_color},"
            f"{self.play_effect},"
            f"{self.effect_speed},"
            f"{self.duration},"
            f"{self.play_count},"
            f"{self.text},"
            f"{self.is_play_text_voice},"
            f"{self.is_sync_play},"
            f"{self.voice_sound},"
            f"{self.volume},"
            f"{self.voice_speed},"
            f"{self.intonation}"
        )

        return protocol


class _ImageMedia(BaseMedia):
    file_path: str  # 图片文件路径
    flash: str  # 闪烁

    def __str__(self) -> str:
        protocol_1 = (
            f"img{self._index}="
            f"{self.x},"
            f"{self.y},"
            f"{self.file_path},"
            f"{self.flash},"
            f"{self.width},"
            f"{self.height}"
        )
        protocol_2 = (
            f"imgparam{self._index}="
            f"{self.duration},"
            f"0,"  # 占位符
            f"00,"  # 动画类型
            f"1,"  # 播放次数
            f"1"
        )  # 动画时长

        protocol = protocol_1 + CRLF + protocol_2
        return protocol


class _WebMedia(BaseMedia):
    url: HttpUrl  # url地址
    refresh_time: int  # 刷新时间，单位100ms 为0时不刷新

    def __str__(self) -> str:
        protocol = (
            f"webview{self._index}="
            f"{self.x},"
            f"{self.y},"
            f"{self.url},"
            f"{self.refresh_time},"
            f"{self.width},"
            f"{self.height}"
        )
        return protocol


# ==============================================================================
# 媒体构造类
# ==============================================================================
class TextMediaBuilder(BaseMediaBuilder):
    """文本构造器

    Args:
        BaseMediaBuilder (_type_): _description_
    """

    def __init__(self):
        super().__init__()
        self.font: str = FontEnum.HEI_TI.value
        self.text_size: int = 1616
        self.text_color: str = ColorEnum.RED.value
        self.background_color: str = ColorEnum.BLACK.value
        self.text: str = ""
        self.flash: str = "0"
        self.font_style: str = FontStyleEnum.NORMAL.value
        self.world_space: int = 0
        self.alignment_direction: str = AlignEnum.HORIZONTAL.value

    def build(self) -> BaseMedia:
        media = _TextMedia(**self.__dict__)
        media._index = self._index
        return media


class TextextMediaBuilder(BaseMediaBuilder):
    """扩展文本构造器

    Args:
        BaseMediaBuilder (_type_): _description_
    """

    def __init__(self):
        super().__init__()
        self.font: str = FontEnum.HEI_TI.value
        self.text_size: int = 1616
        self.font_style: str = FontStyleEnum.NORMAL.value
        self.horizontal_alignment: str = HorizontalAlignmentEnum.CENTER.value
        self.vertical_alignment: str = VerticalAlignmentEnum.CENTER.value
        self.line_space: int = 1
        self.word_space: int = 0
        self.text_color: str = ColorEnum.RED.value
        self.background_color: str = ColorEnum.BLACK.value
        self.play_effect: str = PlayEffectEnum.NONE.value
        self.effect_speed: str = EffectSpeedEnum.NORMAL.value
        self.play_count: int = 1
        self.text: str = ""
        self.is_play_text_voice: str = IsPlayTextVoiceEnum.NO.value
        self.is_sync_play: str = IsSyncPlayEnum.NO.value
        self.voice_sound: str = VoiceSoundEnum.COMMON_FEMALE_VOICE.value
        self.volume: int = 5
        self.voice_speed: int = 5
        self.intonation: int = 5

    def build(self) -> BaseMedia:
        media = _TextextMedia(**self.__dict__)
        media._index = self._index
        return media


class ImageMediaBuilder(BaseMediaBuilder):
    def __init__(self):
        super().__init__()
        self.file_path: str = ""
        self.flash: str = "0"

    def build(self):
        media = _ImageMedia(**self.__dict__)
        media._index = self._index
        return media


class WebMediaBuilder(BaseMediaBuilder):
    def __init__(self):
        super().__init__()
        self.url: str = ""
        self.refresh_time: int = 0

    def build(self) -> BaseMedia:
        media = _WebMedia(**self.__dict__)
        media._index = self._index
        return media


# ==============================================================================
# 播放项
# ==============================================================================


class _Item(BaseModel):
    """播放项，即表示单个页面"""

    _media_list: List[BaseMedia] = PrivateAttr(default_factory=list)
    _auto_media_index: NonNegativeInt = PrivateAttr(
        default_factory=int
    )  # item内媒体序号，默认从0开始，自动累加，不应该被修改

    _index: NonNegativeInt = PrivateAttr(default_factory=int)  # item序号

    duration: NonNegativeInt  # 停留时间， 默认单位是100ms
    screen_in: str  # 入屏方式
    screen_out: str  # 出屏方式
    screen_speed: str  # 入屏速度
    flash_speed: str  # 闪烁速度
    flash_count: str  # 闪烁次数
    play_count: str  # 播放次数

    def __str__(self):
        protocol = f"[item{self._index}]"
        protocol += CRLF
        param = (
            f"param={self.duration},"
            f"{self.screen_in},"
            f"{self.screen_out},"
            f"{self.screen_speed},"
            f"{self.flash_speed},"
            f"{self.flash_count},"
            f"{self.play_count}"
        )
        protocol += param
        protocol += CRLF

        for media in self._media_list:
            protocol += str(media)
            protocol += CRLF

        return protocol


class ItemBuilder:
    def __init__(self):
        self._media_list: List[BaseMedia] = []
        self._auto_media_index: int = 0
        self._index: int = 0
        self.duration: int = 100
        self.screen_in: str = "1"
        self.screen_out: str = "1"
        self.screen_speed: str = "1"
        self.flash_speed: str = "0"
        self.flash_count: str = "5"
        self.play_count: str = "1"

    def add_media_builder(self, media_builder: BaseMediaBuilder) -> "ItemBuilder":
        """可在此处扩展公共参数，每个媒体的私有参数，请在创建媒体build的时候扩展

        :param media_builder:
        :return:
        """
        self._auto_media_index += 1
        media_builder._index = self._auto_media_index
        media_builder.duration = self.duration
        media = media_builder.build()
        self._media_list.append(media)

        return self

    def build(self):
        item = _Item(**self.__dict__)
        # * 由于pydantic对私有属性的限制，对于私有属性只能通过赋值，不能通过构造
        item._index = self._index
        item._media_list = self._media_list
        item._auto_media_index = self._auto_media_index
        return item


# ==============================================================================
# 播放文件
# ==============================================================================


class _Play(BaseModel):
    """播放文件类

    Args:
        BaseModel (_type_): _description_

    Raises:
        ValueError: _description_

    Returns:
        _type_: _description_
    """

    _item_list: List[_Item] = PrivateAttr(default_factory=list)  # 播放节目集合
    _auto_item_index: NonNegativeInt = PrivateAttr(default_factory=int)
    push_protocol: str  # 播放节目对应的直接指令, 暂时没用到
    play_id: int = Field(
        ..., gt=0, le=100
    )  # 节目id，一般不指定，默认1，支持播放列表1-100


    def __str__(self) -> str:
        """play播放文件字符串"""
        if not self._item_list:
            raise ValueError("item_list is empty")

        protocol = "[all]"
        protocol += CRLF
        protocol += f"items={len(self._item_list)}"
        protocol += CRLF

        for item in self._item_list:
            protocol += str(item)
        return protocol


class PlayBuilder:
    """播放文件类构造器"""

    def __init__(self):
        self._item_list: List[_Item] = []
        self.push_protocol: str = ""
        self.play_id: int = 1
        self._auto_item_index: int = 0

    def add_item_builder(self, item_builder: ItemBuilder) -> "PlayBuilder":
        self._auto_item_index += 1
        item_builder._index = self._auto_item_index
        item = item_builder.build()
        self._item_list.append(item)

        return self

    def build(self) -> _Play:
        play = _Play(**self.__dict__)
        # * 由于pydantic对私有属性的限制，对于私有属性只能通过赋值，不能通过构造
        play._auto_item_index = self._auto_item_index
        play._item_list = self._item_list
        return play


# ==============================================================================
# 解析器
# ==============================================================================


class BaseParser:
    """解析器基类"""
    @classmethod
    @abstractmethod
    def parse(cls, data: bytes) -> Any:
        pass


class PlayParser(BaseParser):
    """播放文件解析器

    播放文件格式：
    [all]
    items=2
    [item1]
    param=100,1,1,1,0,5,1,0,1
    txt1=10,0,3,1616,1,8,0,车牌：冀A318AA大货车,192,320,0
    txtparam1=0,0
    [item2]
    param=100,1,1,1,0,5,1,0,1
    txt1=10,0,3,1616,1,8,0,车牌：冀A318AA大货车,192,320,0
    txtparam1=0,0

    Args:
        BaseParser (_type_): _description_
    """

    @classmethod
    def parse(cls, data: str) -> PlayBuilder:
        config = configparser.ConfigParser()
        config.read_string(data)
        play_builer = PlayBuilder()
        item_num = int(config.get("all", "items"))

        for i in range(1, item_num + 1):
            section = f"item{i}"
            section_config = configparser.ConfigParser()
            section_config[section] = dict(config[section])
            with io.StringIO() as f:
                section_config.write(f)
                item = f.getvalue()
                
            item_builder = ItemParser.parse(item)
            play_builer.add_item_builder(item_builder)
        return play_builer


class ItemParser(BaseParser):
    """播放项解析器

    播放项格式
    [item1]
    param=100,1,1,1,0,5,1,0,1
    txt1=10,0,3,1616,1,8,0,车牌：冀A318AA大货车,192,320,0
    txtparam1=0,0

    Args:
        BaseParser (_type_): _description_
    """
    TXT_PATTERN = re.compile(r"^txt\d+$")
    TXT_PARAM_PATTERN = re.compile(r"^txtparam\d+$")
    TXTEXT_PATTERN = re.compile(r"^txtext\d+$")
    IMAGE_PATTERN = re.compile(r"^img\d+$")
    IMAGE_PARAM_PATTERN = re.compile(r"^imgparam\d+$")
    @classmethod
    def parse(cls, data: str) -> ItemBuilder:
        config = configparser.ConfigParser()

        config.read_string(data)

        item_builder = ItemBuilder()
        item_name = config.sections()[0]

        text_cache, img_cache = {}, {}

        options = config.options(item_name)  # noqa: F811
        for option in options:
            match option:
                case "param":
                    param = config.get(item_name, "param")
                    params = param.split(",")
                    item_builder.duration = int(params[0])
                    item_builder.screen_in = params[1]
                    item_builder.screen_out = params[2]
                    item_builder.screen_speed = params[3]
                    item_builder.flash_speed = params[4]
                    item_builder.flash_count = params[5]
                    item_builder.play_count = params[6]

                case _ if cls.TXT_PATTERN.match(option):  # 文本媒体
                    index = re.search(r"\d+", option).group()  
                    if index not in text_cache:
                        text_cache[index] = TextMediaBuilder()

                    text = config.get(item_name, option)
                    fields = text.split(",")
                    text_builder = text_cache[index]
                    text_builder.x = int(fields[0])
                    text_builder.y = int(fields[1])
                    text_builder.font = fields[2]
                    text_builder.text_size = int(fields[3])
                    text_builder.text_color = fields[4]
                    text_builder.background_color = fields[5]
                    text_builder.flash = fields[6]
                    text_builder.text = fields[7]
                    text_builder.width = int(fields[8])
                    text_builder.height = int(fields[9])
                    text_builder.font_style = fields[10]

                case _ if cls.TXT_PARAM_PATTERN.match(option):  # 文本参数媒体
                    index = re.search(r"\d+", option).group()  
                    if index not in text_cache:
                        text_cache[index] = TextMediaBuilder()

                    text = config.get(item_name, option)
                    fields = text.split(",")
                    text_builder = text_cache[index]
                    text_builder.world_space = int(fields[0])
                    text_builder.alignment_direction = fields[1]

                case _ if cls.TXTEXT_PATTERN.match(option):  # 扩展文本媒体
                    textext = config.get(item_name, option)
                    fields = textext.split(",")
                    textext_builder = TextextMediaBuilder()
                    textext_builder.x = int(fields[0])
                    textext_builder.y = int(fields[1])
                    textext_builder.width = int(fields[2])
                    textext_builder.height = int(fields[3])
                    textext_builder.font = fields[4]
                    textext_builder.text_size = int(fields[5])
                    textext_builder.font_style = fields[6]
                    textext_builder.horizontal_alignment = fields[7]
                    textext_builder.vertical_alignment = fields[8]
                    textext_builder.line_space = int(fields[9])
                    textext_builder.word_space = int(fields[10])
                    textext_builder.text_color = fields[11]
                    textext_builder.background_color = fields[12]
                    textext_builder.play_effect = fields[13]
                    textext_builder.effect_speed = fields[14]
                    textext_builder.duration = int(fields[15])
                    textext_builder.play_count = int(fields[16])
                    textext_builder.text = fields[17]
                    textext_builder.is_play_text_voice = fields[18]
                    textext_builder.is_sync_play = fields[19]
                    textext_builder.voice_sound = fields[20]
                    textext_builder.volume = int(fields[21])
                    textext_builder.voice_speed = int(fields[22])
                    textext_builder.intonation = int(fields[23])
                    item_builder.add_media_builder(textext_builder)

                case _ if cls.IMAGE_PATTERN.match(option):  # 图片媒体
                    index = re.search(r"\d+", option).group()  
                    if index not in img_cache:
                        img_cache[index] = ImageMediaBuilder()

                    img = config.get(item_name, option)
                    fields = img.split(",")
                    img_builder = img_cache[index]
                    img_builder.x = int(fields[0])
                    img_builder.y = int(fields[1])
                    img_builder.file_path = fields[2]
                    img_builder.flash = fields[3]
                    img_builder.width = int(fields[4])
                    img_builder.height = int(fields[5])

                case _ if cls.IMAGE_PARAM_PATTERN.match(option):
                    index = re.search(r"\d+", option).group()  
                    if index not in img_cache:
                        img_cache[index] = ImageMediaBuilder()

                    img = config.get(item_name, option)
                    fields = img.split(",")
                    img_builder: ImageMediaBuilder = img_cache[index]
                    img_builder.duration = int(fields[0])

        for builder in text_cache.values():
            item_builder.add_media_builder(builder)
        for builder in img_cache.values():
            item_builder.add_media_builder(builder)

        return item_builder
