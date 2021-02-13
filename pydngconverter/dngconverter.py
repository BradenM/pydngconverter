# -*- coding: utf-8 -*-

"""PyDNGConverter interface bridges for Adobe DNG Converter."""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Iterator

from pydngconverter.flags import DNGVersion, CRawCompat, Compression, JPEGPreview


@dataclass
class DNGParameters:
    """Adobe DNG Converter Parameters."""

    # Enable lossy DNG Compression.
    compression: Compression = Compression.NO
    # Camera RAW Compatible Version.
    camera_raw: CRawCompat = CRawCompat.latest()
    # DNG Version.
    dng_version: DNGVersion = DNGVersion.latest()
    # JPEG thumbnail preview quality.
    jpeg_preview: JPEGPreview = JPEGPreview.MEDIUM
    # Embed fast load data.
    fast_load: bool = False
    # Linear DNG.
    linear: bool = False

    @property
    def fast_load_flag(self) -> Optional[str]:
        if self.fast_load:
            return '-fl'

    @property
    def linear_flag(self) -> Optional[str]:
        if self.fast_load:
            return '-l'

    @property
    def iter_args(self) -> Iterator[str]:
        yield self.compression.flag
        yield self.camera_raw.flag
        yield self.dng_version.flag
        if self.fast_load_flag:
            yield self.fast_load_flag
        if self.linear_flag:
            yield self.linear_flag
        if self.jpeg_preview == JPEGPreview.EXTRACT:
            yield JPEGPreview.NONE.flag
        else:
            yield self.jpeg_preview.flag


