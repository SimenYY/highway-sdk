from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict
from .log import LoguruConfig


class LogConfig(BaseSettings):
    """Log configuration"""

    model_config = SettingsConfigDict(
        env_prefix="HIGHWAY_SDK_", env_file=[".env.local", ".env"], extra="allow"
    )

    LOG_NAME: str = "None"
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "DEBUG"
    LOG_ROTATION: str = "00:00"
    LOG_RETENTION: str = "3 days"
    LOG_COMPRESSION: str = "zip"
    LOG_ENQUEUE: bool = True
    LOG_CONSOLE: bool = True
    LOG_FILE: bool = True

    def config_loguru(self) -> None:
        LoguruConfig.intercept_logging()
        config = LoguruConfig(name=self.LOG_NAME, level=self.LOG_LEVEL)
        if self.LOG_CONSOLE:
            config.set_console()
        if self.LOG_FILE:
            config.set_file(
                rotation=self.LOG_ROTATION,
                retention=self.LOG_RETENTION,
                compression=self.LOG_COMPRESSION,
                enqueue=self.LOG_ENQUEUE,
            )
