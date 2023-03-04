"""Utility functions for PyDNGConverter."""

import time
import shutil
import asyncio
import logging
import functools
from typing import Union
from pathlib import Path

logger = logging.getLogger("pydngconverter").getChild("utils")


def locate_program(name):
    """Locates program path by name.

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


def ensure_existing_dir(path: Union[str, Path]):
    """Ensure provided path exists and is a directory.

    Args:
        path: path to check

    Returns:
        Path: Path object.
        NoneType: If path does not exists or is not a directory
    """
    path = Path(path)
    if not path.exists():
        return None
    if not path.is_dir():
        return None
    return path


def timeit(func):  # pragma: no cover
    """Async variant of timeit."""

    async def process(func, *args, **params):
        if asyncio.iscoroutinefunction(func):
            logger.debug(f"this function is a coroutine: {func.__name__}")
            return await func(*args, **params)
        else:
            logger.debug("this is not a coroutine")
            return func(*args, **params)

    async def helper(*args, **params):
        logger.info(f"{func.__name__}.time")
        start = time.time()
        result = await process(func, *args, **params)

        # Test normal function route...
        # result = await process(lambda *a, **p: print(*a, **p), *args, **params)

        logger.info(">>> %s", time.time() - start)
        return result

    return helper


def force_async(fn):  # pragma: no cover
    """execute sync function in 'awaitable' thread."""
    import asyncio
    from concurrent.futures import ThreadPoolExecutor

    pool = ThreadPoolExecutor()

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        future = pool.submit(fn, *args, **kwargs)
        return asyncio.wrap_future(future)  # make it awaitable

    return wrapper
