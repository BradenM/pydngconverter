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
import itertools

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


class DNGConverter:
    """Python Interface to Adobe DNG Converter

    Takes the same parameters as the Adobe DNG Converter, but uses
    enums and such to make it easier to use.

    Args:
        source: Path to source directory containing raw files

    Keyword Args:
        dest: Path to destination.
            Defaults to source directory.
        max_workers: Set maximum number of workers.
            Defaults to CPU core count.
        debug: Enable debug logs and benchmarking.
            Defaults to false.
        **params: DNG Converter parameters.

    Raises:
        FileNotFoundError: DNG Converter cannot be found.
        NotADirectoryError: Source directory does not exist
             or is not a directory.
    """

    def __init__(
        self,
        source: Union[str, Path],
        dest: Optional[PathLike] = None,
        max_workers=None,
        debug=False,
        **params
    ):
        if debug:
            logger.setLevel(logging.DEBUG)
            logging.getLogger("asyncio").setLevel(logging.WARNING)
            # enable benchmarking.
            self.convert = utils.timeit(self.convert)
        self.parameters = DNGParameters(**params)
        self.bin_path, self.bin_exec = compat.resolve_executable(
            ["Adobe DNG Converter", "dngconverter"], "PYDNG_DNG_CONVERTER"
        )
        if self.parameters.jpeg_preview == JPEGPreview.EXTRACT:
            self.exif_path, self.exif_exec = compat.resolve_executable(
                ["exiftool"], "PYDNG_EXIF_TOOL"
            )
        self.source: Path = Path(source)
        self.source = utils.ensure_existing_dir(self.source)
        if not self.source:
            raise NotADirectoryError(f"{source} does not exists or is not a directory!")
        self.source = self.source.absolute()
        self.job = dngconverter.DNGBatchJob(
            source_directory=self.source, dest_directory=Path(dest) if dest else None
        )
        self.max_workers = max_workers or psutil.cpu_count()
        self._loop = asyncio.get_event_loop()
        self._queue = asyncio.Queue(loop=self._loop)

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

        log.info(
            "[bold white]extracting raw thumbnail:[/] [bold grey58]%s => %s[/]",
            job.source.name,
            job.thumbnail_filename,
        )
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
        log.info(
            "[b white]converting:[/] [bold grey58]%s => %s[/]",
            job.source.name,
            job.destination_filename,
        )
        proc = await asyncio.create_subprocess_exec(
            self.bin_exec, *dng_args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        await proc.wait()
        log.info(
            "[bold bright_green]finished conversion:[/][bold white] %s[/]", job.destination_filename
        )
        return job.destination

    async def create_worker(self, name: str):
        """Create job execution worker.

        Args:
            name: friendly name for worker.

        """
        worker_log = logger.getChild(name)
        results = []
        while True:
            try:
                worker_log.debug("worker awaiting job (qsize: %s)...", self._queue.qsize())
                item = await self._queue.get()
                job, action, kwargs = item
                worker_log.debug("received job: %s (%s)", job, action)
                _result = await action(job=job, **kwargs, log=worker_log)
                results.append(_result) if _result else None
                worker_log.debug("worker finished job!")
                self._queue.task_done()
            except asyncio.CancelledError:
                worker_log.info("terminating...")
                break
        return results

    async def convert(self):
        """Recursively convert all files in source directory."""
        destination = await compat.get_compat_path(self.job.jobs[0].destination.parent)
        # queue up jobs.
        for job in self.job.jobs:
            logger.debug("queueing job: %s", job.source.name)
            self._queue.put_nowait((job, self.convert_file, dict(destination=destination)))
            if self.will_extract:
                self._queue.put_nowait((job, self.extract_thumbnail, dict()))

        tasks = []
        logger.debug("creating %s workers!", self.max_workers)
        # create n workers to execute jobs.
        for i in range(self.max_workers):
            task = asyncio.create_task(self.create_worker(f"worker{i}"))
            tasks.append(task)

        # wait for all jobs to be completed.
        await self._queue.join()

        logger.debug("queue empty! terminating workers...")
        for task in tasks:
            task.cancel()

        # wait until everything is cleaned up.
        _results = await asyncio.gather(*tasks, return_exceptions=True)

        results = list(itertools.chain.from_iterable(_results))
        logger.debug("Job completed. Results: %s", results)
        logger.info(
            "[bold bright_green]Job completed.[/][bold white] %s files were generated.[/]",
            len(results),
        )
        return results
