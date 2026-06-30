"""日志模块。

提供开箱即用的 loguru 日志配置，简化开发者使用。
"""

import inspect
import logging
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import loguru


@dataclass
class LoggerConfig:
    """日志配置。

    Args:
        name: 日志名称，用于命名日志文件
        level: 日志级别，默认为 "DEBUG"
        log_dir: 日志文件目录，默认为 None（不输出文件）
        serialize: 是否使用 JSON 格式输出，默认为 False
        rotation: 日志文件轮转规则，默认为 "00:00"
        retention: 日志保留时间，默认为 "3 days"
        compression: 日志压缩格式，默认为 "zip"
    """

    name: str
    level: str = "DEBUG"
    log_dir: str | None = None
    serialize: bool = False
    rotation: str = "00:00"
    retention: str = "3 days"
    compression: str = "zip"


class _PrefixLoggerAdapter(logging.LoggerAdapter):
    def __init__(self, logger, *, prefix: str | None = None):
        extra = {"prefix": prefix} if prefix else None
        super().__init__(logger, extra)

    def process(self, msg, kwargs):
        if self.extra and "prefix" in self.extra:
            return f"{self.extra['prefix']} - {msg}", kwargs
        return super().process(msg, kwargs)


class _PropagateHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        logging.getLogger(record.name).handle(record)


class _InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = loguru.logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = inspect.currentframe(), 0
        while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1

        loguru.logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def _setup_default_logger() -> None:
    """设置默认日志配置。"""
    loguru.logger.remove()
    loguru.logger.add(
        sys.stdout,
        level="DEBUG",
        format=(
            "<level>{level: <8}</level> | "
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
        ),
    )


_setup_default_logger()


def get_logger(name: str, **kwargs) -> Any:
    """获取配置好的 loguru logger。

    Args:
        name: 日志名称
        **kwargs: 日志配置参数，覆盖默认配置

    Returns:
        loguru.Logger: 配置好的 logger 实例

    Example:
        >>> from highway_sdk.core.log import get_logger
        >>> logger = get_logger("my_app", level="INFO")
        >>> logger.info("Hello, world!")
    """
    config = LoggerConfig(name=name, **kwargs)

    if config.log_dir:
        log_dir = Path(config.log_dir) / config.name
        log_dir.mkdir(parents=True, exist_ok=True)
        loguru.logger.add(
            str(log_dir / f"{config.name}_{{time:YYYY-MM-DD}}.log"),
            level=config.level,
            rotation=config.rotation,
            retention=config.retention,
            compression=config.compression,
            serialize=config.serialize,
            enqueue=True,
        )

    return loguru.logger.bind(name=config.name)


def intercept_logging(namespaces: list[str] | None = None) -> None:
    """拦截指定的 logging 命名空间到 loguru。

    Args:
        namespaces: 要拦截的命名空间列表，None/空列表表示不拦截，["*"]表示全部拦截
    """
    handler = _InterceptHandler()

    logging.basicConfig(handlers=[], level=logging.WARNING, force=True)
    for logger_name in logging.root.manager.loggerDict:
        logger = logging.getLogger(logger_name)
        logger.handlers.clear()
        logger.propagate = True

    if not namespaces:
        return

    if "*" in namespaces:
        logging.basicConfig(handlers=[handler], level=0, force=True)
    else:
        for namespace in namespaces:
            logger = logging.getLogger(namespace)
            logger.setLevel(0)
            logger.handlers.clear()
            logger.addHandler(handler)
            logger.propagate = False

            for existing_name in logging.root.manager.loggerDict:
                if existing_name.startswith(namespace + "."):
                    sub_logger = logging.getLogger(existing_name)
                    sub_logger.setLevel(0)
                    sub_logger.handlers.clear()
                    sub_logger.addHandler(handler)
                    sub_logger.propagate = False


class LoguruConfig:
    """向后兼容的 loguru 配置类。"""

    def __init__(self, name: str, level: str = "DEBUG", serialize: bool = False):
        self._config = LoggerConfig(name=name, level=level, serialize=serialize)

    def set_console(self) -> None:
        pass

    def set_file(
        self,
        log_dir: str = "logs",
        *,
        split_by_name: bool = True,
        rotation: str = "00:00",
        retention: str = "3 days",
        compression: str = "zip",
        enqueue: bool = True,
    ):
        self._config.log_dir = log_dir
        self._config.rotation = rotation
        self._config.retention = retention
        self._config.compression = compression

    def include_logging_namespace(self, namespace: str) -> None:
        intercept_logging([namespace])

    def exclude_logging_namespace(self, namespace: str) -> None:
        pass

    def clear_all_intercepts(self) -> None:
        intercept_logging([])

    def propagate_logging(self) -> None:
        loguru.logger.add(_PropagateHandler())

    @classmethod
    def intercept_logging(cls, namespaces: list[str] | None = None) -> None:
        intercept_logging(namespaces)

    @classmethod
    def reset_logging(cls) -> None:
        logging.basicConfig(handlers=[], level=logging.WARNING, force=True)
        for logger_name in logging.root.manager.loggerDict:
            logger = logging.getLogger(logger_name)
            logger.handlers.clear()
            logger.propagate = True


LogConfig = LoguruConfig


def setup_logger(name: str = "highway_sdk", level: str = "DEBUG", **kwargs) -> LoguruConfig:
    """向后兼容的日志设置函数。"""
    return LoguruConfig(name=name, level=level, **kwargs)


PrefixLoggerAdapter = _PrefixLoggerAdapter
