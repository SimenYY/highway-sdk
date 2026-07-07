import sys
from collections.abc import Callable
from functools import partial, wraps
from pathlib import Path
from typing import Any

from filelock import AsyncFileLock, BaseAsyncFileLock, BaseFileLock, FileLock
from platformdirs import user_data_dir

from highway_sdk.core.log import get_logger

logger = get_logger(__name__)

__all__ = ["AppLock"]


class AppLock:
    """应用锁，防止应用二次启动

    这个类的作用是通过文件锁来实现同一个时间只能运行一个应用

    Attributes:
        name (str): 应用名称
        lock_file (str): 文件锁文件名
        lock (BaseFileLock | BaseAsyncFileLock): 文件锁对象

    """

    def __init__(self, name: str = "app") -> None:
        self.name: str = name
        lock_dir = Path(user_data_dir(appname=name))
        lock_dir.mkdir(parents=True, exist_ok=True)
        self.lock_file: Path = lock_dir / "app.lock"
        self.lock: BaseAsyncFileLock | BaseFileLock | None = None
        logger.info(f"lock file path: {self.lock_file!s}")

    @classmethod
    def lock_this(cls, main: Callable[..., Any] | None = None, *, name: str = "app"):
        """应用锁函数装饰器

        Args:
            main (Callable[..., Any] | None, optional): 应用入口函数. Defaults to None.
            name (str, optional): 应用名称. Defaults to "app".

        Example:
        ... @AppLock.lock_this
        ... def main():
        ...     print("hello world")

        ... @AppLock.lock_this(name="myapp")
        ... def main():
        ...     print("hello world")
        """
        if main is None:
            return partial(cls.lock_this, name=name)

        @wraps(main)
        def _lock_this(*args, **kwargs):
            with cls(name):
                return main(*args, **kwargs)

        return _lock_this

    @classmethod
    def async_lock_this(cls, main: Callable[..., Any] | None = None, *, name: str = "app"):
        """异步应用锁函数装饰器

        Args:
            main (Callable[..., Any] | None, optional): 应用入口函数. Defaults to None.
            name (str, optional): 应用名称. Defaults to "app".

        Example:
        ... @AppLock.async_lock_this
        ... def main():
        ...     print("hello world")

        ... @AppLock.async_lock_this(name="myapp")
        ... def main():
        ...     print("hello world")
        """
        if main is None:
            return partial(cls.async_lock_this, name=name)

        @wraps(main)
        async def _async_lock_this(*args, **kwargs):
            async with cls(name):
                return await main(*args, **kwargs)

        return _async_lock_this

    def __enter__(self):
        try:
            self.lock = FileLock(self.lock_file)
            self.lock.acquire(timeout=0)
            logger.info("The app is started successfully")
        except TimeoutError:
            logger.warning("The app is already running")
            sys.exit(0)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if isinstance(self.lock, FileLock):
            self.lock.release()
            self.lock = None
        else:
            raise TypeError("文件锁类型错误：期望 FileLock 实例")
        logger.info("应用已正常退出")

        if exc_type is not None:
            logger.error(f"上下文执行异常：{exc_val}")

    async def __aenter__(self):
        try:
            self.lock = AsyncFileLock(self.lock_file)
            await self.lock.acquire(timeout=0)
            logger.info("The app is started successfully")
        except TimeoutError:
            logger.warning("The app is already running")
            sys.exit(0)

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if isinstance(self.lock, AsyncFileLock):
            await self.lock.release()
            self.lock = None
        else:
            raise TypeError("文件锁类型错误：期望 AsyncFileLock 实例")
        logger.info("应用已正常退出")

        if exc_type is not None:
            logger.error(f"上下文执行异常：{exc_val}")
