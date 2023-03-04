"""PyDNGConverter Compatibility module.

Handles platform-specific operations.
"""

import os
import asyncio
import logging
import platform
from copy import deepcopy
from enum import Enum, auto
from typing import List, Union, Optional
from pathlib import Path

from pydngconverter import utils

logger = logging.getLogger("pydngconverter").getChild("utils")


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


async def _exec_wine(winecmd: str, *args):
    """Execute wine command.

    Will check for WINEPREFIX in user env, defaulting to ~/.dngconverter
    (AUR package default path) if it is not provided.
    """
    prefix = os.environ.get("WINEPREFIX", Path.home() / ".dngconverter" / "wine")
    logger.debug("wine prefix: %s", prefix)
    prefix = Path(prefix)
    wineenv = dict(**deepcopy(os.environ), **dict(WINEPREFIX=str(prefix)))
    logger.debug("Executing [italic white]%s %s[/]", winecmd, " ".join(args))
    proc = await asyncio.create_subprocess_exec(
        winecmd, *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, env=wineenv
    )
    stdout, _ = await proc.communicate()
    return stdout


async def wine_path(unix_path: Path) -> str:
    """Convert *nix path to Windows path."""
    win_path = await _exec_wine("winepath", "-w", str(unix_path))
    win_path = win_path.decode().rstrip("\n")
    return win_path


async def get_compat_path(path: Union[str, Path]) -> str:
    """Convert given path to a DNGConverter compatible format.

    DNGConverter requires Windows-like paths on *nix environments that
    utilize wine.
    """
    _path = Path(path)
    plat = Platform.get()

    if plat.is_unknown:
        # at least try instead of failing.
        logger.warning("unable to determine platform! defaulting to linux.")
        return str(_path)

    if plat.is_nix:
        # dngconverter runs in wine on *nix,
        # but it requires windows-type paths.
        _path = await wine_path(_path)
        logger.debug("converted unix to windows path: %s", _path)
        return _path

    return str(_path)


def resolve_executable(name_variants: List[str], env_override: Optional[str] = None) -> str:
    """Resolve platform-specific path to given executable.

    Args:
        name_variants: List of executable names to look for.
        env_override: Environment variable name to use as override if available.

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
        Platform.LINUX: "{name}",
        Platform.WINDOWS: "{name}.exe",
        Platform.DARWIN: "{name}.app/Contents/MacOS/{name}",
    }

    # oh, look at me. fancy walrus operator :)
    if env_override and (override_path := os.environ.get(env_override)):
        override_path = Path(override_path.strip())
        if override_path.exists():
            logger.info("using binary path override from %s: %s", env_override, override_path)
            # allow use of env vars to override paths in case of resolution failure.
            return override_path

    def _resolve(names: List[str]) -> Path:
        for name in names:
            _app_root = app_map.get(plat, app_map[Platform.LINUX])
            _app_ext = app_ext.get(plat, app_ext[Platform.LINUX]).format(name=name)
            _app_path = _app_root / _app_ext
            if _app_path.exists():
                yield name, _app_path
            try:
                bin_path = utils.locate_program(name)
            except Exception:
                pass
            else:
                if bin_path is not None:
                    yield name, bin_path

    try:
        name, exec_path = next(_resolve(name_variants))
    except StopIteration as e:
        raise RuntimeError(
            f"Could not locate {', '.join(name_variants)} binary! You can manually provide a path with the {env_override} env "
            "variable. "
        ) from e
    else:
        logger.info("resolved executable for: %s @ %s", name, exec_path)
        return exec_path
