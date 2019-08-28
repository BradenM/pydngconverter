# -*- coding: utf-8 -*-

"""
pydngconverter.utils
====================================
Utility functions for PyDNGConverter
"""

import shutil
from pathlib import Path


def locate_program(name):
    """Locates program path by name

    Args:
        name (str): Name of executable

    Returns:
        pathlib.Path: Pathlike Object to Program
        NoneType: If no suitable path is found
    """
    prog_path = shutil.which(name)
    if not prog_path:
        return None
    return Path(prog_path)


def ensure_existing_dir(path):
    """Ensure provided path exists and is a directory

    Args:
        path (str): path to check

    Returns:
        pathlib.Path: Pathlike object
        NoneType: If path does not exists or is not a directory
    """
    path = Path(path)
    if not path.exists():
        return None
    if not path.is_dir():
        return None
    return path
