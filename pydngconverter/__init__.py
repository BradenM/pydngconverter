"""
PyDngConverter
====================================
A Python Interface to Adobe's DNG Converter.

Uses parallel processing and Image manipulation to significantly
speed up the process of converting RAW images to DNG.
"""

__author__ = """Braden Mars"""
__version__ = "0.3.0"

from pydngconverter import flags
from pydngconverter.main import DNGConverter, DNGParameters

__all__ = ["DNGConverter", "DNGParameters", "flags"]
