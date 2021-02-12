# -*- coding: utf-8 -*-
"""PyDNGConverter Compatibility module.

Handles platform-specific operations.

"""

import platform
from enum import Enum, auto
from pathlib import Path
from typing import Union, List, Tuple
import os
import subprocess as subp
from pydngconverter import utils
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


def resolve_executable(name_variants: List[str]) -> Tuple[Path, str]:
    """Resolve platform-specific path to given executable.

    Args:
        name_variants: List of executable names to look for.

    Returns:
        Path to executable and platform-specific command to execute.
    """
    plat = Platform.get()
    app_map = {
        Platform.LINUX: Path("/usr/bin"),
        Platform.WINDOWS: Path(r"C:\Program Files"),
        Platform.DARWIN: Path("/Applications"),
    }
    app_ext = {
        Platform.LINUX: "{}",
        Platform.WINDOWS: "{}.exe",
        Platform.DARWIN: "{}.app/Contents/MacOS/{}",
    }
    app_exec = {
        Platform.LINUX: "{}",
        Platform.WINDOWS: "{}",
        Platform.DARWIN: 'open -a "{}" --args',
    }

    def _resolve(names: List[str]) -> Path:
        for name in names:
            _app_root = app_map.get(plat, app_map[Platform.LINUX])
            _app_ext = app_ext.get(plat, app_map[Platform.LINUX]).format(name)
            _app_path = _app_root / _app_ext
            if _app_path.exists():
                yield _app_path
            try:
                bin_path = utils.locate_program(name)
            except Exception:
                pass
            else:
                if bin_path is not None:
                    yield bin_path

    try:
        exec_path = next(_resolve(name_variants))
    except StopIteration as e:
        raise RuntimeError(
            "Could not locate DNG Converter binary! You can manually provide a path with the PYDNG_CONVERTER_PATH env "
            "variable. "
        ) from e
    else:
        return exec_path, app_exec.get(plat, app_ext[Platform.LINUX]).format(str(exec_path))
