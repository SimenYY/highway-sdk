"""日志模块。

第三方库只提供日志接口，不配置日志输出。
应用应该使用 logging 或 loguru 统一配置所有日志。
"""

import logging


def get_logger(name: str) -> logging.Logger:
    """获取绑定了库名称的 logger。

    Args:
        name: 日志名称，用于标识日志来源

    Returns:
        绑定了 name 的 logging logger

    Example:
        >>> from highway_sdk.core.log import get_logger
        >>> logger = get_logger("highway_sdk.transport")
        >>> logger.info("Connected to device")
    """
    return logging.getLogger(name)
