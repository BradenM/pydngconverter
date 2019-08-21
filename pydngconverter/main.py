# -*- coding: utf-8 -*-

"""Main module."""

from enum import Enum

from pydngconverter import utils


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
    NONE = 0
    MEDIUM = 1
    FULL = 2

    @property
    def name(self):
        return "p"


class CRawCompat(CliFlag):
    TWO_FOUR = 2.4
    FOUR_ONE = 4.1
    FOUR_SIX = 4.6
    FIVE_FOUR = 5.4
    SIX_SIX = 6.6
    SEVEN_ONE = 7.1

    @property
    def name(self):
        return "cr"


class DNGVersion(CliFlag):
    ONE_ONE = 1.1
    ONE_THREE = 1.3
    ONE_FOUR = 1.4

    @property
    def name(self):
        return "dng"


class DNGConverter:
    def __init__(self,
                 source,
                 dest=None,
                 compressed=True,
                 camera_raw=CRawCompat.latest(),
                 dng_version=DNGVersion.latest()):
        self.prog_path = utils.locate_program("dngconverter")
        self.compressed = compressed
        self.camera_raw = camera_raw
        self.dng_version = dng_version

        if not self.prog_path:
            raise FileNotFoundError("DNGConverter is not installed!")
        self.source = utils.ensure_existing_dir(source)
        if not self.source:
            raise NotADirectoryError(
                f"{source} does not exists or is not a directory!")
