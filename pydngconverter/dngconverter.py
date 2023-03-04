"""PyDNGConverter interface bridges for Adobe DNG Converter."""

from typing import List, Iterator, Optional
from pathlib import Path
from dataclasses import field, dataclass

from pydngconverter.flags import CRawCompat, DNGVersion, Compression, JPEGPreview, LossyCompression


@dataclass
class DNGParameters:
    """Adobe DNG Converter Parameters.

    Attributes:
        compression (flags.DNGVersion): Enable DNG compression.
            Defaults to true.
        camera_raw (flags.CRawCompat): Camera RAW compatibility version.
            Defaults to latest.
        dng_version (flags.DNGVersion): DNG backwards compatible version.
            Defaults to latest.
        jpeg_preview (flags.JPEGPreview): JPEG preview thumbnail quality/method.
            Defaults to medium quality.
        fast_load (bool): Embed fast load data.
            Defaults to false.
        lossy (flags.LossyCompression): Enable lossy compression.
            Defaults to `flags.LossyCompression.NO`.
        side (int): Long-side pixels (32-65000). Implies lossy compression.
        count (int): Megapixels limit of >= 1024 (1MP). Implies lossy compression.
        linear (bool): Enable linear DNG format.
            Defaults to false.
    """

    compression: Compression = Compression.YES
    camera_raw: CRawCompat = CRawCompat.latest()
    dng_version: DNGVersion = DNGVersion.latest()
    jpeg_preview: JPEGPreview = JPEGPreview.MEDIUM
    fast_load: bool = False
    lossy: LossyCompression = LossyCompression.NO
    side: Optional[int] = 0
    count: Optional[int] = 0
    linear: bool = False

    @property
    def fast_load_flag(self) -> Optional[str]:
        if self.fast_load:
            return "-fl"

    @property
    def linear_flag(self) -> Optional[str]:
        if self.linear:
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
            yield "-side"
            yield f"{self.side}"
        if self.count:
            yield "-count"
            yield f"{self.count}"
        if self.jpeg_preview == JPEGPreview.EXTRACT:
            yield JPEGPreview.NONE.flag
        else:
            yield self.jpeg_preview.flag


@dataclass
class DNGJob:
    """DNG Conversion job.

    Attributes:
        source: Job source image path.
        destination_root: Job destination directory.
            Defaults to source path root.
        _parent: Parent Job.
            Defaults to None.
    """

    source: Path
    destination_root: Path = None
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
    """Batch DNG Conversion.

    Attributes:
        source_directory: Directory of source images.
        jobs: Child jobs of this batch job.
            Automatically populated based on source directory.
        dest_directory: Destination directory.
            Defaults to source directory root.
    """

    source_directory: Path
    jobs: List[DNGJob] = field(default_factory=list)
    dest_directory: Optional[Path] = None

    def __post_init__(self):
        files = [f for f in self.source_directory.rglob("*") if f.is_file()]
        self.jobs = [DNGJob(f, destination_root=self.dest_directory, _parent=self) for f in files]
        return self
