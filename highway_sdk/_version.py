from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("highway_sdk")
except PackageNotFoundError:
    __version__ = "unknown"
