import inspect
import logging
import sys
from pathlib import Path
from typing import Final

import loguru

# ==============================================================================
# logger adapter
# ==============================================================================


class PrefixLoggerAdapter(logging.LoggerAdapter):
    """Add external prefix to log messages.

    Args:
        logging (logging.Logger): _description_

    Examples:
    >>> logger = logger.getLogger(__name__)
    ... logger = PrefixLoggerAdapter(logger, prefix="your prefix")
    """

    def __init__(self, logger, *, prefix: str | None = None):
        if prefix:
            extra = {"prefix": prefix}
        else:
            extra = None
        super().__init__(logger, extra)

    def process(self, msg, kwargs):
        if self.extra and "prefix" in self.extra:
            return f"{self.extra['prefix']} - {msg}", kwargs

        return super().process(msg, kwargs)


# ==============================================================================
# logging hander
# ==============================================================================


class PropagateHandler(logging.Handler):
    """Propagate loguru messages to logging

    Usage:
        logger.add(PropagateHandler(), format="{message}")
    """

    def emit(self, record: logging.LogRecord) -> None:
        logging.getLogger(record.name).handle(record)


class InterceptHandler(logging.Handler):
    """
    Default handler from examples in loguru documentation.

    This handler intercepts all log requests and
    passes them to loguru.

    For more info see:
    https://loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-with-standard-logging
    """

    def emit(self, record: logging.LogRecord) -> None:
        # Get corresponding Loguru level if it exists.
        level: str | int
        try:
            level = loguru.logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message.
        frame, depth = inspect.currentframe(), 0
        while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1

        loguru.logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


class ColoredStreamHandler(logging.StreamHandler):
    """Colored stream handler"""

    def __init__(self):
        super().__init__()
        try:
            from colorlog import ColoredFormatter
        except ImportError:
            raise ImportError("colorlog is not installed")

        self.setFormatter(
            ColoredFormatter(
                "%(green)s%(asctime)s.%(msecs)03d"
                "%(red)s | "
                "%(log_color)s%(levelname)-8s"
                "%(red)s | "
                "%(cyan)s%(name)s"
                "%(red)s:"
                "%(cyan)s%(module)s"
                "%(red)s:"
                "%(cyan)s%(funcName)s"
                "%(red)s:"
                "%(cyan)s%(lineno)d"
                "%(red)s - "
                "%(log_color)s%(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
                reset=True,
                log_colors={
                    "DEBUG": "blue",
                    "INFO": "white",
                    "WARNING": "yellow",
                    "ERROR": "red",
                    "CRITICAL": "white,bg_red",
                },
                style="%",
            )
        )


# ==============================================================================
# logging utils
# ==============================================================================
class LoguruConfig:
    """loguru配置类，用于配置日志输出格式、位置和拦截规则

    Example:
        >>> from highway_sdk.core.log import LoguruConfig
        >>>
        >>> # 基本配置
        >>> log_config = LoguruConfig(name="my_app", level="INFO")
        >>> log_config.set_console()
        >>> log_config.set_file()
        >>>
        >>> # 配置JSON格式日志
        >>> log_config = LoguruConfig(name="my_app", level="INFO", serialize=True)
        >>> log_config.set_console()
        >>>
        >>> # 配置日志轮转
        >>> log_config.set_file(
        ...     log_dir="logs",
        ...     rotation="100 MB",  # 按大小轮转
        ...     retention="7 days",  # 保留7天
        ...     compression="zip"  # 压缩格式
        ... )
        >>>
        >>> # 动态控制命名空间
        >>> log_config.include_logging_namespace("app.module1")
        >>> log_config.exclude_logging_namespace("third_party_lib")
        >>>
        >>> # 清除所有拦截配置
        >>> log_config.clear_all_intercepts()
        >>>
        >>> # 拦截所有logging命名空间
        >>> LoguruConfig.intercept_logging(["*"])
        >>>
        >>> # 仅拦截指定命名空间
        >>> LoguruConfig.intercept_logging(["app.module1", "app.module2"])
        >>>
        >>> # 不拦截任何命名空间
        >>> LoguruConfig.intercept_logging([])
        >>>
        >>> # 重置logging配置
        >>> LoguruConfig.reset_logging()
        >>>
        >>> # 启用loguru到logging的传播
        >>> log_config.propagate_logging()
    """

    DEFAULT_FORMAT: Final = (
        "<level>{level: <8}</level> | "
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )

    def __init__(
        self,
        name: str,
        level: str = "DEBUG",
        serialize: bool = False,  # 与loguru一致的参数名
    ):
        """初始化loguru配置

        Args:
            name: 日志名称，用于命名日志文件
            level: 日志级别，默认为"DEBUG"
            serialize: 是否使用JSON格式输出，默认为False

        Example:
            >>> # 基本初始化
            >>> log_config = LoguruConfig(name="my_app")
            >>>
            >>> # 自定义日志级别
            >>> log_config = LoguruConfig(name="my_app", level="INFO")
            >>> log_config = LoguruConfig(name="my_app", level="WARNING")
            >>> log_config = LoguruConfig(name="my_app", level="ERROR")
            >>>
            >>> # 配置JSON格式输出
            >>> log_config = LoguruConfig(name="my_app", serialize=True)
            >>>
            >>> # 组合配置
            >>> log_config = LoguruConfig(name="my_app", level="INFO", serialize=True)
        """
        loguru.logger.remove()

        self.name = name
        self.level = level
        self.serialize = serialize
        self._included_loggers = set()
        self._excluded_loggers = set()

    @classmethod
    def intercept_logging(cls, namespaces: list[str] | None = None) -> None:
        """拦截指定的logging命名空间到loguru

        Args:
            namespaces: 要拦截的命名空间列表，如果为None或空列表，则不拦截任何命名空间
                        使用["*"]表示拦截所有命名空间

        Example:
            >>> # 拦截所有命名空间
            >>> LoguruConfig.intercept_logging(["*"])
            >>>
            >>> # 仅拦截特定命名空间
            >>> LoguruConfig.intercept_logging(["app", "third_party"])
            >>>
            >>> # 拦截主命名空间及其子命名空间
            >>> LoguruConfig.intercept_logging(["app.module1"])
            >>> # 此时app.module1和app.module1.submodule都会被拦截
        """
        intercept_handler = InterceptHandler()

        # 先重置所有logger的配置
        cls.reset_logging()

        if namespaces is None or not namespaces:
            # 不拦截任何命名空间，保持默认配置
            return

        if "*" in namespaces:
            # 拦截所有命名空间
            logging.basicConfig(handlers=[intercept_handler], level=0, force=True)
        else:
            # 仅拦截指定命名空间
            for namespace in namespaces:
                logger = logging.getLogger(namespace)
                logger.setLevel(0)
                logger.handlers.clear()
                logger.addHandler(intercept_handler)
                logger.propagate = False

                # 确保子命名空间也能被拦截
                # 例如，拦截"app.module1"时，"app.module1.submodule"也会被拦截
                for existing_name in logging.root.manager.loggerDict:
                    if existing_name.startswith(namespace + "."):
                        sub_logger = logging.getLogger(existing_name)
                        sub_logger.setLevel(0)
                        sub_logger.handlers.clear()
                        sub_logger.addHandler(intercept_handler)
                        sub_logger.propagate = False

    @classmethod
    def reset_logging(cls) -> None:
        """重置logging配置到默认状态

        Example:
            >>> # 重置logging配置
            >>> LoguruConfig.reset_logging()
            >>>
            >>> # 重置后，所有logger恢复默认行为
            >>> import logging
            >>> logger = logging.getLogger("app.module1")
            >>> logger.setLevel(logging.INFO)
            >>> logger.info("这条日志使用默认logging配置输出")
        """
        logging.basicConfig(handlers=[], level=logging.WARNING, force=True)
        # 清除所有logger的handlers
        for logger_name in logging.root.manager.loggerDict:
            logger = logging.getLogger(logger_name)
            logger.handlers.clear()
            logger.propagate = True

    def propagate_logging(self) -> None:
        """将所有loguru日志传播到logging模块

        Example:
            >>> # 启用loguru到logging的传播
            >>> log_config.propagate_logging()
            >>>
            >>> # 此时loguru日志会同时输出到logging系统
            >>> import loguru
            >>> logger = loguru.logger
            >>> logger.info("这条日志会同时输出到logging")
        """
        loguru.logger.add(PropagateHandler(), format=self.DEFAULT_FORMAT)

    def include_logging_namespace(self, namespace: str) -> None:
        """添加logging命名空间到拦截列表

        Args:
            namespace: 要拦截的命名空间

        Example:
            >>> # 添加单个命名空间
            >>> log_config.include_logging_namespace("app.module1")
            >>>
            >>> # 添加多个命名空间
            >>> log_config.include_logging_namespace("app.module2")
            >>> log_config.include_logging_namespace("app.module3")
        """
        logging_logger = logging.getLogger(namespace)
        self.include_logging_logger(logging_logger)
        self._included_loggers.add(namespace)

        # 如果该命名空间在排除列表中，将其移除
        if namespace in self._excluded_loggers:
            self._excluded_loggers.remove(namespace)

    def include_logging_logger(self, logging_logger: logging.Logger) -> None:
        """添加logging.logger到拦截列表

        Args:
            logging_logger: 要拦截的logger对象

        Example:
            >>> import logging
            >>>
            >>> # 获取一个logger对象
            >>> my_logger = logging.getLogger("app.custom")
            >>>
            >>> # 拦截该logger
            >>> log_config.include_logging_logger(my_logger)
        """
        logging_logger.setLevel(self.level)
        logging_logger.handlers.clear()
        logging_logger.addHandler(InterceptHandler())
        logging_logger.propagate = False

    def exclude_logging_namespace(self, namespace: str) -> None:
        """从拦截列表中排除指定的logging命名空间

        Args:
            namespace: 要排除的命名空间

        Example:
            >>> # 排除单个命名空间
            >>> log_config.exclude_logging_namespace("third_party_lib")
            >>>
            >>> # 排除多个命名空间
            >>> log_config.exclude_logging_namespace("debug_module")
            >>> log_config.exclude_logging_namespace("verbose_module")
        """
        logging_logger = logging.getLogger(namespace)
        self.exclude_logging_logger(logging_logger)
        self._excluded_loggers.add(namespace)

        # 如果该命名空间在包含列表中，将其移除
        if namespace in self._included_loggers:
            self._included_loggers.remove(namespace)

    def exclude_logging_logger(self, logging_logger: logging.Logger) -> None:
        """从拦截列表中排除指定的logging.logger

        Args:
            logging_logger: 要排除的logger对象

        Example:
            >>> import logging
            >>>
            >>> # 获取一个logger对象
            >>> my_logger = logging.getLogger("app.custom")
            >>>
            >>> # 排除该logger
            >>> log_config.exclude_logging_logger(my_logger)
        """
        # 清除该logger的所有handler，恢复默认行为
        logging_logger.handlers.clear()
        logging_logger.propagate = True
        # 设置为默认级别，避免过多日志
        logging_logger.setLevel(logging.WARNING)

    def clear_all_intercepts(self) -> None:
        """清除所有拦截配置，恢复默认logging行为

        Example:
            >>> # 清除所有拦截配置
            >>> log_config.clear_all_intercepts()
            >>>
            >>> # 清除后，logging日志不再被拦截
            >>> import logging
            >>> logger = logging.getLogger("app.module1")
            >>> logger.info("这条日志不会被loguru拦截")
        """
        # 重置logging配置
        logging.basicConfig(handlers=[], level=logging.WARNING, force=True)

        # 清除所有logger的handlers
        for logger_name in logging.root.manager.loggerDict:
            logger = logging.getLogger(logger_name)
            logger.handlers.clear()
            logger.propagate = True
            logger.setLevel(logging.NOTSET)

        # 清空包含和排除列表
        self._included_loggers.clear()
        self._excluded_loggers.clear()

    def set_console(self) -> None:
        """配置控制台输出，支持JSON格式

        Example:
            >>> # 配置控制台输出
            >>> log_config.set_console()
            >>>
            >>> # 配置JSON格式控制台输出
            >>> json_config = LoguruConfig(name="my_app", level="INFO", serialize=True)
            >>> json_config.set_console()
        """
        loguru.logger.add(
            sys.stdout,
            level=self.level,
            serialize=self.serialize,  # 使用与loguru一致的参数名
        )

    def set_file(
        self,
        log_dir: Path | str = "logs",
        *,
        split_by_name: bool = True,
        rotation: str = "00:00",
        retention: str = "3 days",
        compression: str = "zip",
        enqueue: bool = True,
    ):
        """配置文件输出，支持JSON格式

        Args:
            log_dir: 日志目录
            split_by_name: 是否按logger名称分目录存储
            rotation: 日志文件轮转规则，可以是时间或大小，如"00:00"或"100 MB"
            retention: 日志保留时间，如"7 days"或"1 month"
            compression: 日志压缩格式，如"zip"或"gz"
            enqueue: 是否使用异步写入

        Example:
            >>> # 基本文件输出配置
            >>> log_config.set_file()
            >>>
            >>> # 自定义日志目录
            >>> log_config.set_file(log_dir="custom_logs")
            >>>
            >>> # 按大小轮转日志
            >>> log_config.set_file(rotation="100 MB")
            >>>
            >>> # 按时间轮转日志
            >>> log_config.set_file(rotation="00:00")  # 每天凌晨轮转
            >>> log_config.set_file(rotation="1 hour")  # 每小时轮转
            >>>
            >>> # 自定义日志保留时间
            >>> log_config.set_file(retention="14 days")  # 保留14天
            >>> log_config.set_file(retention="1 month")  # 保留1个月
            >>>
            >>> # 配置日志压缩
            >>> log_config.set_file(compression="zip")  # ZIP压缩
            >>> log_config.set_file(compression="gz")  # GZIP压缩
            >>>
            >>> # 禁用异步写入
            >>> log_config.set_file(enqueue=False)
            >>>
            >>> # 组合配置
            >>> log_config.set_file(
            ...     log_dir="logs",
            ...     rotation="50 MB",
            ...     retention="7 days",
            ...     compression="zip"
            ... )
        """
        log_dir = Path(log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)
        if split_by_name:
            log_file = log_dir / self.name / (f"{self.name}" + "_{time:YYYY-MM-DD}.log")
        else:
            log_file = log_dir / (f"{self.name}" + "_{time:YYYY-MM-DD}.log")
        loguru.logger.add(
            str(log_file),
            level=self.level,
            rotation=rotation,
            retention=retention,
            compression=compression,
            enqueue=enqueue,
            serialize=self.serialize,  # 使用与loguru一致的参数名
        )
