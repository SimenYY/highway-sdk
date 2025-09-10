from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("highway_sdk")
except PackageNotFoundError:
    __version__ = "unknown"
    
    
print(__version__)
