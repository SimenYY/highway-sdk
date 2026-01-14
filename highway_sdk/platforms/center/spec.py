from enum import Enum


class DeviceTypeEnum(Enum):
    VD = (1, 999)  # 0001~0999 车辆检测器
    AERO = (1001, 1099)  # 气象检测器
    VI = (1101, 1199)  # 能见度检测器
    CMS = (1201, 1399)  # 可变情报板
    CSLS = (1401, 1599)  # 可变限速标志
    ET = (2001, 2899)  # 紧急电话

    def __init__(self, min_code, max_code):
        self.min_code = min_code
        self.max_code = max_code

    @classmethod
    def from_code(cls, code: int) -> "DeviceTypeEnum":
        """根据编码返回对应的设备类型枚举"""
        if not isinstance(code, int) or code < 1 or code > 9999:
            raise ValueError(f"Invalid device code: {code}. Must be integer between 1 and 9999.")

        for device_type in cls:
            if device_type.min_code <= code <= device_type.max_code:
                return device_type

        # 如果落在空隙区间（如 1000, 1100 等），视为无效
        raise ValueError(f"Device code {code} is not assigned to any valid type (falls in gap).")

    def contains(self, code: int) -> bool:
        """判断该类型是否包含指定编码"""
        return self.min_code <= code <= self.max_code

    def __str__(self):
        return self.name
