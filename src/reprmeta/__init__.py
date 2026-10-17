""" Python Package API File for ReprMeta """

from importlib.metadata import version, PackageNotFoundError

# Package version
try:
    __version__ = version("reprmeta")
except PackageNotFoundError:
    __version__ = None

# Public API
from .core import get_metadata, print_metadata, export_metadata, render_metadata

__all__ = [
    "get_metadata",
    "print_metadata",
    "export_metadata",
    "render_metadata",
    "__version__",
]
