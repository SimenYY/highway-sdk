import ipaddress
import re
from typing import Final

# ==============================================================================
# 正则编译
# ==============================================================================
_CHAINAGE_PATTERN: Final[re.Pattern] = re.compile(r"^[ZY]?K\d+\+\d{1,3}(\.\d{1,2})?$", re.IGNORECASE)


# ==============================================================================
# judge 函数
# ==============================================================================
def is_ip(ip: str) -> bool:
    """判断是否为IP地址

    Args:
        ip (str): _description_

    Returns:
        bool: _description_
    """
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False


def is_user_port(port: int | str) -> bool:
    """判断是否是用户可用的port，1024~65535

    Args:
        port (int | str): _description_

    Returns:
        bool: _description_
    """
    return str(port).isdigit() and 1024 <= int(port) <= 65535


def is_chainage(chainage: str):
    """
    判断是否是合法的桩号（支持 K / ZK / YK 格式，Z/Y 可有可无）

    支持的格式示例：
        K123+456
        K12+345.67
        ZK123+456
        YK12+345.6
        zk123+000      （大小写不敏感）
        yK123+456.78
    """
    return bool(_CHAINAGE_PATTERN.match(str(chainage).strip()))
