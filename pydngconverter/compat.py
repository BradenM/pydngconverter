# -*- coding: utf-8 -*-
"""PyDNGConverter Compatibility module.

Handles platform-specific operations.

"""

import platform
from enum import Enum, auto
from pathlib import Path
from typing import Union
import os
import subprocess as subp
from copy import deepcopy


class Platform(Enum):
    UNKNOWN = auto()  # fallback
    UNIX = auto()
    SOLARIS = auto()
    LINUX = auto()
    WINDOWS = auto()
    DARWIN = auto()

    @property
    def is_unknown(self) -> bool:
        return self == Platform.UNKNOWN

    @property
    def is_nix(self) -> bool:
        return self in [Platform.LINUX, Platform.UNIX, Platform.SOLARIS]

    @property
    def is_darwin(self) -> bool:
        return self == Platform.DARWIN

    @property
    def is_win(self) -> bool:
        return self == Platform.WINDOWS

    @classmethod
    def get(cls) -> "Platform":
        return getattr(cls, str(platform.system()).upper())


def _exec_wine(winecmd: str, *args):
    """Execute wine command.

    Will check for WINEPREFIX in user env,
    defaulting to ~/.dngconverter (AUR package default path)
    if it is not provided.

    """
    prefix = os.environ.get("WINEPREFIX", Path.home() / ".dngconverter" / "wine")
    prefix = Path(prefix)
    _base_cmd = [winecmd]
    _base_cmd.extend(args)
    wineenv = dict(**deepcopy(os.environ), **dict(WINEPREFIX=str(prefix)))
    return subp.run(_base_cmd, env=wineenv, text=True, stdout=subp.PIPE)


def wine_path(unix_path: Path) -> str:
    """Convert *nix path to Windows path."""
    proc = _exec_wine("winepath", "-w", str(unix_path))
    _path = proc.stdout.strip()
    return _path


def get_compat_path(path: Union[str, Path]) -> str:
    """Convert given path to a DNGConverter compatible format.

    DNGConverter requires Windows-like paths on *nix environments
    that utilize wine.

    """
    _path = Path(path)
    plat = Platform.get()

    if plat.is_unknown:
        # at least try instead of failing.
        return str(_path)

    if plat.is_nix:
        # dngconverter runs in wine on *nix,
        # but it requires windows-type paths.
        return wine_path(_path)

    return str(_path)
