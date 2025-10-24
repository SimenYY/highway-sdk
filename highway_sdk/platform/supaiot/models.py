from typing import Dict, Optional, List, Any, Union
from pydantic import BaseModel, Field
from pydantic.config import ConfigDict


class _ApiResult(BaseModel):
    resultCode: str
    resultError: str


class SupaiotResponse(BaseModel):
    data: Union[Dict[Any, Any], List[Any]]
    result: _ApiResult


class _baseSupaiotRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)


class DeviceListRequest(_baseSupaiotRequest):
    """条件查询设备列表的请求体
    对应平台接口 /supaiot/api/v2/device/list 的 body
    """

    page_num: int = Field(..., alias="pageNum", description="请求页码")
    page_size: int = Field(..., alias="pageSize", description="每页条数")

    device_ids: Optional[List[str]] = Field(None, alias="ID", description="设备实例ID列表")
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

class DeviceRealtimeDataListRequest(_baseSupaiotRequest):
    device_ids: List[str] = Field(..., alias="ID", description="设备ID列表")
