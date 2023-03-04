"""PyDNGConverter Flag Enums.

Provides mappings for Adobe DNG Converter's parameters.

See Also:
    Command Line Support in the Adobe DNG Converter:
        https://wwwimages2.adobe.com/content/dam/acom/en/products/photoshop/pdfs/dng_commandline.pdf
"""

from enum import Enum


class CliFlag(Enum):
    @property
    def name(self):
        return ""

    @property
    def flag(self):
        return f"-{self.name}{self.value}"

    @classmethod
    def latest(cls):
        return list(cls)[-1]


class JPEGPreview(CliFlag):
    """JPEG Preview/Thumbnail.

    Setting to "Extract" will
    extract a thumbnail via the raw image's exif data.

    All other options are passed and handled via Adobe DNG Converter.
    """

    NONE = 0
    MEDIUM = 1
    FULL = 2
    EXTRACT = 3

    @property
    def name(self):
        return "p"


class CRawCompat(CliFlag):
    """Camera Raw Compatibility version."""

    TWO_FOUR = 2.4
    FOUR_ONE = 4.1
    FOUR_SIX = 4.6
    FIVE_FOUR = 5.4
    SIX_SIX = 6.6
    SEVEN_ONE = 7.1
    ELEVEN_TWO = 11.2
    TWELVE_FOUR = 12.4
    THIRTEEN_TWO = 13.2
    FOURTEEN = 14.0

    @property
    def name(self):
        return "cr"


class DNGVersion(CliFlag):
    """DNG backwards compatibility version."""

    ONE_ONE = 1.1
    ONE_THREE = 1.3
    ONE_FOUR = 1.4
    ONE_SIX = 1.6

    @property
    def name(self):
        return "dng"


class Compression(CliFlag):
    """DNG Lossless Compression."""

    NO = "u"
    YES = "c"


class LossyCompression(CliFlag):
    """DNG Lossy Compression."""

    NO = ""
    YES = "-lossy"

    @property
    def flag(self):
        if self == Compression.YES:
            return "-lossy"
        return ""
