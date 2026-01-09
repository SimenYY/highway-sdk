from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field, field_serializer, field_validator
from pydantic.networks import IPvAnyAddress
from pydantic.config import ConfigDict
from highway_sdk.utils.judge import is_chainage

__all__ = [
    "APIResponse",
    "BaseAPIRequest",
    "Devices",
    "DevicesRealtimeData",
    "ClassListRequest",
    "BaseMqttModel",
    "ControlReqSubscribeModel",
    "_ControlReqCommandModel",
    "RealtimeDataPublishModel",
    "HistoryDataPublishModel",
    "DeviceInfoMode",
]


# ==============================================================================
# API Models
# ==============================================================================
class _ApiResult(BaseModel):
    resultCode: str
    resultError: str


class APIResponse(BaseModel):
    data: dict[Any, Any] | list[Any] | None
    result: _ApiResult


class BaseAPIRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)


class Devices(BaseAPIRequest):
    """条件查询设备列表的请求体
    对应平台接口 /supaiot/api/v2/device/list 的 body
    """

    page_num: int = Field(..., alias="pageNum", description="请求页码")
    page_size: int = Field(..., alias="pageSize", description="每页条数")

    device_ids: list[str] | None = Field(None, alias="ID", description="设备实例ID列表")
    app_id: str | None = Field(None, alias="appId", description="应用ID")
    area_id: str | None = Field(None, alias="areaID", description="区域ID")
    class_id: str | None = Field(None, alias="classID", description="原型ID")
    class_name: str | None = Field(None, alias="className", description="原型名称")
    class_type: str | None = Field(None, alias="classType", description="设备类型")
    label: list[dict] | None = Field(None, alias="label", description="标签")
    name: str | None = Field(None, description="设备名称")
    project_id: str | None = Field(None, alias="projectID", description="项目ID")
    sub_off: bool | None = Field(
        None,
        alias="subOff",
        description="是否包含子集 默认false，只显示当前区域，true包含子集区域数据",
    )
    type_: str | None = Field(None, alias="type", description="类型")


class DevicesRealtimeData(BaseAPIRequest):
    device_ids: list[str] = Field(..., alias="ID", description="设备ID列表")


class ClassListRequest(BaseAPIRequest):
    """条件查询设备原型列表"""

    page_num: int = Field(..., alias="pageNum", description="请求页码")
    page_size: int = Field(..., alias="pageSize", description="每页条数")
    detail_level: int | None = Field(None, alias="detailLevel", description="详情等级")
    class_id: str | None = Field(None, alias="classID", description="原型ID")
    class_type: str | None = Field(None, alias="classType", description="设备类型")
    label: list[dict] | None = Field(None, alias="label", description="标签")
    name: str | None = Field(None, description="设备名称")
    project_id: str | None = Field(None, alias="projectID", description="项目ID")
    type_: str | None = Field(None, alias="type", description="类型")


# ==============================================================================
# MQTT Models
# ==============================================================================
class BaseMqttModel(BaseModel):
    """物联智控MQTT Model 基类"""

    time: datetime = Field(default_factory=datetime.now, description="推送时间")

    @field_serializer("time")
    def serialize_time(self, time: datetime) -> str:
        return time.strftime("%Y-%m-%d %H:%M:%S")

    def get_topic(self):
        """获取对应的主题

        Returns:
            str: _description_
        """


class ControlReqSubscribeModel(BaseMqttModel):
    """设备订阅控制命令

    用于校验

    Args:
        SupaiotMqttModel (_type_): _description_

    Returns:
        _type_: _description_
    """

    series: str = Field(..., description="设备产品序列号")
    sn: str = Field(..., description="设备标识码")
    version: str = Field(..., description="设备版本号")
    timestamp: int | None = Field(default=None, description="Unix毫秒级推送时间")
    needResponse: bool = Field(..., description="是否需要设备响应控制命令")
    sequence: int = Field(..., description="命令序列号")
    data: dict = Field(..., description="可下发单条或者多条控制命令")

    @classmethod
    def get_topic(cls, series: str, sn: str, version: str = "1.0") -> str:
        """获取主题

        一般是要先订阅主题

        Args:
            series (str): _description_
            sn (str): _description_
            version (str, optional): _description_. Defaults to "1.0".

        Returns:
            str: _description_
        """
        return f"/edge/{series}/{sn}/{version}/control"


class _ControlReqCommandModel(BaseModel):
    """控制响应命令

    用于构建

    Args:
        BaseModel (_type_): _description_
    """

    time: datetime = Field(default_factory=datetime.now, description="响应时间")
    timestamp: int | None = Field(default=None, description="Unix毫秒级推送时间")
    value: Any = Field(..., description="控制数值")
    succes: bool = Field(..., description="控制命令是否下发成功")
    resultCode: int = Field(..., description="控制结果序号，等于0成功，非0失败")
    resultMsg: str = Field(..., description="控制结果描述（失败原因")


class ControlRespPublishModel(BaseMqttModel):
    """设备响应控制命令


    注：（必填）data.time、data.value、data.succes、data.resultcode
            data.resultMsg
    """

    series: str = Field(..., description="设备产品序列号")
    sn: str = Field(..., description="设备标识码")
    version: str = Field(default="1.0", description="协议版本号")
    sequence: int = Field(..., description="命令序列号")
    data: dict[str, _ControlReqCommandModel] = Field(
        ..., description="可响应单条或者多条控制命令"
    )

    def get_topic(self) -> str:
        return f"/edge/{self.series}/{self.sn}/{self.version}/response"


class RealtimeDataPublishModel(BaseMqttModel):
    """设备上报实时数据

    用于构建
    """

    series: str = Field(..., description="设备产品序列号")
    sn: str = Field(..., description="设备标识码")
    version: str = Field(default="1.0", description="协议版本号")
    timestamp: int | None = Field(
        default=None,
        description="Unix毫秒级推送时间",
    )
    data: dict = Field(..., description="设备运行数据")

    def get_topic(self):
        return f"/edge/{self.series}/{self.sn}/{self.version}/data"


class _HistoryDataModel(BaseModel):
    """推送历史数据

    Args:
        BaseModel (_type_): _description_
    """

    time: datetime = Field(default_factory=datetime.now, description="推送时间")
    timestamp: int | None = Field(default=None, description="Unix毫秒级推送时间")

    model_config = ConfigDict(extra="allow")


class HistoryDataPublishModel(BaseMqttModel):
    """设备推送历史数据"""

    series: str = Field(..., description="设备产品序列号")
    sn: str = Field(..., description="设备标识码")
    version: str = Field(default="1.0", description="协议版本号")
    data: list[_HistoryDataModel] = Field(..., description="推送历史数据列表")

    def get_topic(self):
        return f"/edge/{self.series}/{self.sn}/{self.version}/history"


# ==============================================================================
# Bussiness models
# ==============================================================================
class DeviceInfoMode(BaseModel):
    """业务设备信息模型"""

    series: str = Field(..., description="设备产品序列号")
    sn: str = Field(..., description="设备标识码")
    port: int | None = Field(default=None, description="设备端口号")
    ip: IPvAnyAddress = Field(..., description="设备IP地址")
    device_id: str | None = Field(default=None, description="设备编码")
    class_id: str | None = Field(default=None, description="设备原型ID")
    chainage: str | None = Field(default=None, description="设备桩号")
    extra: dict[str, Any] = Field(default_factory=dict, description="扩展字段")

    @field_validator("chainage")
    @classmethod
    def validate_chainage(cls, value: str | None) -> str | None:
        if value is not None:
            if not is_chainage(value):
                raise ValueError(f"Invalid chainage, input: {value}")
        return value
