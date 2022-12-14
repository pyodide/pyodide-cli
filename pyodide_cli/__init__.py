from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("pyodide-cli")
except PackageNotFoundError:
    # package is not installed
    pass
