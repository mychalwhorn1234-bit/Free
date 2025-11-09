"""
FORScan Python automation package.

This package provides Python tools for automating FORScan diagnostics,
data analysis, and integration with external systems.
"""

__version__ = "0.1.0"
__author__ = "FORScan Automation Team"
__email__ = ""

from .core import FORScanConnector
from .adapters import ELM327Adapter, J2534Adapter
from .diagnostics import DiagnosticSession
from .config import Config

__all__ = [
    "FORScanConnector",
    "ELM327Adapter", 
    "J2534Adapter",
    "DiagnosticSession",
    "Config",
]