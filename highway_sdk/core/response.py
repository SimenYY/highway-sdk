"""统一响应格式模块。

所有设备功能接口均返回 ``Response`` 结构，提供统一的成功/失败语义。
"""

from pydantic import BaseModel, Field


class Response(BaseModel):
    """统一响应格式。

    所有设备功能接口均返回此结构。

    Attributes:
        status: 响应状态，仅 ``"success"`` / ``"error"`` 两种。
        error_msg: 错误信息。成功时为 ``None``，失败时携带可读的错误描述。
        data: 响应数据。成功时携带业务数据，失败时为 ``None``。
    """

    status: str = Field(
        ...,
        description="响应状态：'success' — 操作成功；'error' — 操作失败",
        examples=["success", "error"],
    )
    error_msg: str | None = Field(
        default=None,
        description="错误信息。status='success' 时为 None，status='error' 时为可读错误描述",
        examples=[None, "设备 192.168.1.100:9000 通信超时（30s）"],
    )
    data: dict | None = Field(
        default=None,
        description="响应数据。status='success' 时携带业务数据，status='error' 时为 None",
    )

    @classmethod
    def success(cls, data: dict | None = None) -> "Response":
        """快速构造成功响应。

        Args:
            data: 业务数据。

        Returns:
            Response: status="success" 的响应。
        """
        return cls(status="success", error_msg=None, data=data)

    @classmethod
    def error(cls, error_msg: str) -> "Response":
        """快速构造失败响应。

        Args:
            error_msg: 可读的错误描述。

        Returns:
            Response: status="error" 的响应。
        """
        return cls(status="error", error_msg=error_msg, data=None)
