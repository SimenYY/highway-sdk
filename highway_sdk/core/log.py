import logging
import inspect
from pathlib import Path
import sys
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

        loguru.logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


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
class LoguruUtils:
    DEFAULT_FORMAT: Final = (
        "<level>{level: <8}</level> | "
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )

    @classmethod
    def intercept_logging(cls) -> None:
        """intercept all logging to loguru"""
        intercept_handler = InterceptHandler()
        # Configuares global logging
        logging.basicConfig(handlers=[intercept_handler], level=0, force=True)

    @classmethod
    def propagate_logging(cls) -> None:
        """propagate all loguru to logging"""
        loguru.logger.add(PropagateHandler(), format=cls.DEFAULT_FORMAT)


# ==============================================================================
# logging config
# ==============================================================================
class LoguruConfig:
    """配置loguru

    注释：
        1. 能够添加拦截原生的logger
        2. 能够配置console和file两种常用输出
    """

    def __init__(
        self,
        name: str,
        level: str = "DEBUG",
    ):
        loguru.logger.remove()

        self.name = name
        self.level = level

    def include_logging_namespace(self, namespace: str) -> None:
        """
        添加logging命名空间
        """
        logging_logger = logging.getLogger(namespace)
        self.include_logging_logger(logging_logger)

    def include_logging_logger(self, logging_logger: logging.Logger) -> None:
        """
        添加logging.logger
        """
        logging_logger.setLevel(self.level)
        logging_logger.handlers.clear()
        logging_logger.addHandler(InterceptHandler())
        logging_logger.propagate = False

    def set_console(self) -> None:
        loguru.logger.add(sys.stdout, level=self.level)

    def set_file(
        self,
        log_dir: Path | str = "logs",
        *,
        rotation: str = "00:00",
        retention: str = "3 days",
        compression: str = "zip",
        enqueue: bool = True,
    ):
        log_dir = Path(log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / self.name / (f"{self.name}" + "_{time: YYYY-MM-DD}.log")
        loguru.logger.add(
            str(log_file),
            level=self.level,
            rotation=rotation,
            retention=retention,
            compression=compression,
            enqueue=enqueue,
        )



