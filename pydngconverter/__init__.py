# -*- coding: utf-8 -*-

"""
PyDngConverter
====================================
A Python Interface to Adobe's DNG Converter.

Uses parallel processing and Image manipulation to significantly
speed up the process of converting RAW images to DNG.
"""

__author__ = """Braden Mars"""
__version__ = "0.2.0"

from pydngconverter.main import DNGConverter, DNGParameters
from pydngconverter import flags

__all__ = ["DNGConverter", "DNGParameters", "flags"]
