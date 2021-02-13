# -*- coding: utf-8 -*-

"""
pydngconverter.main
====================================
PyDNGConverter Code Module
"""

import asyncio
import logging
from os import PathLike
from pathlib import Path
from typing import Optional, Union

import psutil
from rich.logging import RichHandler
from wand.image import Image

from pydngconverter import utils, compat, dngconverter
from pydngconverter.dngconverter import DNGParameters
from pydngconverter.flags import JPEGPreview

logging.basicConfig(
    level=logging.INFO,
    format="[bold bright_white]%(name)s:[/][bright_black] %(message)s[/]",
    datefmt="[%X]",
    handlers=[RichHandler(markup=True)],
)
logger = logging.getLogger("pydngconverter")
logging.getLogger("asyncio").setLevel(logging.WARNING)


class DNGConverter:
    """Python Interface to Adobe DNG Converter

    Takes the same parameters as the Adobe DNG Converter, but uses
    enums and such to make it easier to use.

    Args:
        source: Path to source directory containing raw files

    Keyword Args:
        dest: Path to destination.
            Defaults to source directory.
        **params: DNG Converter parameters.

    Raises:
        FileNotFoundError: DNG Converter cannot be found.
        NotADirectoryError: Source directory does not exist
             or is not a directory.
    """

    def __init__(
        self, source: Union[str, Path], dest: Optional[PathLike] = None, debug=False, **params: DNGParameters
    ):
        if debug:
            logger.setLevel(logging.DEBUG)
            # enable benchmarking.
            self.convert = utils.timeit(self.convert)
        self.parameters = DNGParameters(**params)
        self.bin_path, self.bin_exec = compat.resolve_executable(
            ["Adobe DNG Converter", "dngconverter"], "PYDNG_DNG_CONVERTER"
        )
        if self.parameters.jpeg_preview == JPEGPreview.EXTRACT:
            self.exif_path, self.exif_exec = compat.resolve_executable(["exiftool"], "PYDNG_EXIF_TOOL")
        self.source: Path = Path(source)
        self.source = utils.ensure_existing_dir(self.source)
        if not self.source:
            raise NotADirectoryError(f"{source} does not exists or is not a directory!")
        self.source = self.source.absolute()
        self.job = dngconverter.DNGBatchJob(source_directory=self.source, dest_directory=Path(dest))
        self.chunk_size = psutil.cpu_count()
        self._queue = asyncio.Queue()

    @property
    def will_extract(self) -> bool:
        """Whether to create thumbnail extraction jobs or not."""
        return self.parameters.jpeg_preview == JPEGPreview.EXTRACT

    async def _write_thumbnail(
        self, *, job: dngconverter.DNGJob = None, image_bytes=None, log=None, **kwargs
    ):
        """Writes thumbnail from bytes extracted from raw image.

        Args:
            job: current conversion job.
            image_bytes: image blob data.
            log: logger to use.

        """
        log = log or logger
        log.debug("starting write thumbnail: %s", job.thumbnail_filename)

        @utils.force_async
        def _write(image_blob, img_dest):
            with Image(blob=image_blob) as img:
                img.resize(int(img.width * 0.10), int(img.height * 0.10))
                img.save(filename=str(img_dest))

        await _write(image_bytes, job.thumbnail_destination)
        log.info("[bold cyan]wrote thumbnail:[/][bold white] %s[/]", job.thumbnail_filename)

    async def extract_thumbnail(
        self, *, job: dngconverter.DNGJob = None, log=None, **kwargs
    ) -> Path:
        """Extract jpeg thumbnail from exif data.

        Args:
            job: DNG Converter job.
            log: Logger to use.

        Returns:
            Path to thumbnail.

        """
        log = log or logger

        log.info("[bold white]extracting raw thumbnail:[/] [bold grey58]%s => %s[/]", job.source.name, job.thumbnail_filename)
        exif_args = ["-b", "-previewImage", str(job.source)]
        exif_proc = await asyncio.create_subprocess_exec(
            self.exif_exec,
            *exif_args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await exif_proc.communicate()
        self._queue.put_nowait(
            (
                job,
                self._write_thumbnail,
                dict(image_bytes=stdout),
            )
        )
        log.info("[bright_black]queued thumbnail: %s[/]", job.thumbnail_filename)
        return job.thumbnail_destination

    async def convert_file(
        self, *, destination: str = None, job: dngconverter.DNGJob = None, log=None
    ):
        """Execute provided conversion job.

        Args:
            destination: Output path.
            job: DNG Converter job to run.
            log: Logger to use.

        """
        log = log or logger
        log.debug("starting conversion: [b white]%s[/]", job.source.name)
        source_path = await compat.get_compat_path(job.source)
        log.debug("determined source path: [b white]%s[/]", source_path)
        dng_args = [*self.parameters.iter_args, "-d", destination, str(source_path)]
        log.debug("using converter args: %s", ",".join(dng_args))
        log.info("[b white]converting:[/] [bold grey58]%s => %s[/]", job.source.name, job.destination_filename)
        proc = await asyncio.create_subprocess_exec(
            self.bin_exec, *dng_args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        await proc.wait()
        log.info("[bold bright_green]finished conversion:[/][bold white] %s[/]", job.destination_filename)

    async def create_worker(self, name: str):
        """Create job execution worker.

        Args:
            name: friendly name for worker.

        """
        worker_log = logger.getChild(name)
        while True:
            worker_log.debug("worker awaiting job (qsize: %s)...", self._queue.qsize())
            item = await self._queue.get()
            job, action, kwargs = item
            worker_log.debug("received job: %s (%s)", job, action)
            await action(job=job, **kwargs, log=worker_log)
            worker_log.debug("worker finished job!")
            self._queue.task_done()

    async def convert(self):
        """Recursively convert all files in source directory."""
        destination = await compat.get_compat_path(self.job.jobs[0].destination.parent)
        for job in self.job.jobs:
            logger.debug("queueing job: %s", job.source.name)
            self._queue.put_nowait((job, self.convert_file, dict(destination=destination)))
            if self.will_extract:
                self._queue.put_nowait((job, self.extract_thumbnail, dict()))

        tasks = []
        num_workers = self.chunk_size
        logger.debug("creating %s workers!", num_workers)

        for i in range(num_workers + 1):
            task = asyncio.create_task(self.create_worker(f"worker{i}"))
            tasks.append(task)

        await self._queue.join()
        logger.debug("queue(s) empty! canceling workers...")
        for task in tasks:
            task.cancel()

        await asyncio.gather(*tasks, return_exceptions=True)
