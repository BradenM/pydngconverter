# -*- coding: utf-8 -*-

"""PyDNGConverter interface bridges for Adobe DNG Converter."""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Iterator

from pydngconverter.flags import DNGVersion, CRawCompat, Compression, JPEGPreview, LossyCompression


@dataclass
class DNGParameters:
    """Adobe DNG Converter Parameters."""

    # Enable DNG Compression.
    compression: Compression = Compression.YES
    # Camera RAW Compatible Version.
    camera_raw: CRawCompat = CRawCompat.latest()
    # DNG Version.
    dng_version: DNGVersion = DNGVersion.latest()
    # JPEG thumbnail preview quality.
    jpeg_preview: JPEGPreview = JPEGPreview.MEDIUM
    # Embed fast load data.
    fast_load: bool = False
    # Enable lossy compression.
    lossy: LossyCompression = LossyCompression.NO
    # Long-side pixels (from 32-65000). Implied lossy compression.
    side: Optional[int] = 0
    # Megapixels limit of >= 1024 (1MP)
    count: Optional[int] = 0
    # Linear DNG.
    linear: bool = False

    @property
    def fast_load_flag(self) -> Optional[str]:
        if self.fast_load:
            return "-fl"

    @property
    def linear_flag(self) -> Optional[str]:
        if self.fast_load:
            return "-l"

    @property
    def iter_args(self) -> Iterator[str]:
        yield self.compression.flag
        yield self.camera_raw.flag
        yield self.dng_version.flag
        if self.fast_load_flag:
            yield self.fast_load_flag
        if self.linear_flag:
            yield self.linear_flag
        if not self.lossy and (self.side or self.count):
            # implied lossy if side or count provided.
            yield self.lossy.flag
        if self.side:
            yield f"-side {self.side}"
        if self.count:
            yield f"-count {self.count}"
        if self.jpeg_preview == JPEGPreview.EXTRACT:
            yield JPEGPreview.NONE.flag
        else:
            yield self.jpeg_preview.flag


@dataclass
class DNGJob:
    # Job source image.
    source: Path
    # Job destination directory.
    destination_root: Path = None
    # Job Parent.
    _parent: "DNGBatchJob" = field(default=None, repr=False)

    def __post_init__(self):
        if not self.destination_root:
            self.destination_root = self.source.parent

    @property
    def source_suffix(self) -> str:
        return self.source.suffix

    @property
    def destination_filename(self) -> str:
        return self.source.with_suffix(".dng").name

    @property
    def thumbnail_filename(self) -> str:
        return self.source.with_suffix(".thumb.jpg").name

    @property
    def thumbnail_destination(self) -> Path:
        return self.destination_root / self.thumbnail_filename

    @property
    def destination(self) -> Path:
        return self.destination_root / self.destination_filename


@dataclass
class DNGBatchJob:
    # Source directory.
    source_directory: Path
    # Child jobs.
    jobs: List[DNGJob] = field(default_factory=list)
    # Destination directory.
    dest_directory: Optional[Path] = None

    def __post_init__(self):
        pattern = r".*\.(cr2)"
        files = [
            f
            for f in self.source_directory.rglob("*")
            if re.match(pattern, f.name, flags=re.IGNORECASE)
        ]
        self.jobs = [DNGJob(f, destination_root=self.dest_directory, _parent=self) for f in files]
        return self
