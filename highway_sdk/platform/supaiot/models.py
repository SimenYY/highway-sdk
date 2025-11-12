from abc import abstractmethod
from datetime import datetime
from typing import Dict, Optional, List, Any, Union
from pydantic import BaseModel, Field
from pydantic.config import ConfigDict


# ==============================================================================
# API Models
# ==============================================================================
class _ApiResult(BaseModel):
    resultCode: str
    resultError: str


class SupaiotResponse(BaseModel):
    data: Union[Dict[Any, Any], List[Any]]
    result: _ApiResult


class BaseSupaiotRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)


class DeviceListRequest(BaseSupaiotRequest):
    """条件查询设备列表的请求体
    对应平台接口 /supaiot/api/v2/device/list 的 body
    """

    page_num: int = Field(..., alias="pageNum", description="请求页码")
    page_size: int = Field(..., alias="pageSize", description="每页条数")

    device_ids: Optional[List[str]] = Field(
        None, alias="ID", description="设备实例ID列表"
    )
    app_id: Optional[str] = Field(None, alias="appId", description="应用ID")
    area_id: Optional[str] = Field(None, alias="areaID", description="区域ID")
    class_id: Optional[str] = Field(None, alias="classID", description="原型ID")
    class_name: Optional[str] = Field(None, alias="className", description="原型名称")
    class_type: Optional[str] = Field(None, alias="classType", description="设备类型")
    label: Optional[List[dict]] = Field(None, alias="label", description="标签")
    name: Optional[str] = Field(None, description="设备名称")
    project_id: Optional[str] = Field(None, alias="projectID", description="项目ID")
    sub_off: Optional[bool] = Field(
        None,
        alias="subOff",
        description="是否包含子集 默认false，只显示当前区域，true包含子集区域数据",
    )
    type_: Optional[str] = Field(None, alias="type", description="类型")


class DeviceRealtimeDataListRequest(BaseSupaiotRequest):
    device_ids: List[str] = Field(..., alias="ID", description="设备ID列表")


class ClassListRequest(BaseSupaiotRequest):
    """条件查询设备原型列表"""

    page_num: int = Field(..., alias="pageNum", description="请求页码")
    page_size: int = Field(..., alias="pageSize", description="每页条数")
    detail_level: Optional[int] = Field(
        None, alias="detailLevel", description="详情等级"
    )
    class_id: Optional[str] = Field(None, alias="classID", description="原型ID")
    class_type: Optional[str] = Field(None, alias="classType", description="设备类型")
    label: Optional[List[dict]] = Field(None, alias="label", description="标签")
    name: Optional[str] = Field(None, description="设备名称")
    project_id: Optional[str] = Field(None, alias="projectID", description="项目ID")
    type_: Optional[str] = Field(None, alias="type", description="类型")


# ==============================================================================
# MQTT Models
# ==============================================================================
class SupaiotMqttModel(BaseModel):
    """物联智控MQTT Model 基类"""

    def get_payload(self) -> str:
        """获取对应的载荷

        Returns:
            str: _description_
        """
        return self.model_dump_json()

    @abstractmethod
    def get_topic(self) -> str:
        """获取对应的主题

        Returns:
            str: _description_
        """


# -----------------------------------------------------------------------------
# 设备上报历史数据
# -----------------------------------------------------------------------------
class SubscribeControlReqModel(SupaiotMqttModel):
    """设备上报历史数据

    用于校验

    Args:
        SupaiotMqttModel (_type_): _description_

    Returns:
        _type_: _description_
    """

    series: str = Field(..., description="设备产品序列号")
    sn: str = Field(..., description="设备标识码")
    version: str = Field(..., description="设备版本号")
    time: datetime = Field(..., description="推送时间")
    timestamp: int | None = Field(None, description="Unix毫秒级推送时间")
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


# -----------------------------------------------------------------------------
# 设备响应控制命令
# -----------------------------------------------------------------------------
class ControlReqCommandModel(BaseModel):
    """控制响应命令

    用于构建

    Args:
        BaseModel (_type_): _description_
    """

    time: datetime = Field(..., description="响应时间")
    timestamp: int | None = Field(None, description="Unix毫秒级推送时间")
    value: Any = Field(..., description="控制数值")
    succes: bool = Field(..., description="控制命令是否下发成功")
    resultCode: int = Field(..., description="控制结果序号，等于0成功，非0失败")
    resultMsg: str = Field(..., description="控制结果描述（失败原因")


class PublishControlResMqttModel(SupaiotMqttModel):
    """设备响应控制命令


    注：（必填）data.time、data.value、data.succes、data.resultcode
            data.resultMsg
    """

    series: str = Field(..., description="设备产品序列号")
    sn: str = Field(..., description="设备标识码")
    version: str = Field(default="1.0", description="协议版本号")
    time: datetime = Field(..., description="推送时间")
    sequence: int = Field(..., description="命令序列号")
    data: Dict[str, ControlReqCommandModel] = Field(
        ..., description="可响应单条或者多条控制命令"
    )

    def get_topic(self) -> str:
        return f"/edge/{self.series}/{self.sn}/{self.version}/response"


# -----------------------------------------------------------------------------
# 设备上报实时数据
# -----------------------------------------------------------------------------
class PublishRealMqttModel(SupaiotMqttModel):
    """设备上报实时数据

    用于构建
    """

    series: str = Field(..., description="设备产品序列号")
    sn: str = Field(..., description="设备标识码")
    version: str = Field(default="1.0", description="协议版本号")
    time: datetime = Field(..., description="推送时间")
    timestamp: int | None = Field(None, description="Unix毫秒级推送时间")
    data: dict = Field(..., description="设备运行数据")

    def get_topic(self):
        return f"/edge/{self.series}/{self.sn}/{self.version}/data"


# -----------------------------------------------------------------------------
# 设备推送历史数据
# -----------------------------------------------------------------------------
class HistoryDataModel(BaseModel):
    """推送历史数据

    Args:
        BaseModel (_type_): _description_
    """

    time: datetime = Field(..., description="推送时间")
    timestamp: int | None = Field(None, description="Unix毫秒级推送时间")

    model_config = ConfigDict(extra="allow")


class PublishHistoryModel(SupaiotMqttModel):
    """设备推送历史数据"""

    series: str = Field(..., description="设备产品序列号")
    sn: str = Field(..., description="设备标识码")
    version: str = Field(default="1.0", description="协议版本号")
    time: datetime = Field(..., description="推送时间")
    data: list[HistoryDataModel] = Field(..., description="推送历史数据列表")

    def get_topic(self):
        return f"/edge/{self.series}/{self.sn}/{self.version}/history"
