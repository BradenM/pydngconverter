# -*- coding: utf-8 -*-

"""Main module."""

import subprocess as subproc
from enum import Enum
from pathlib import Path

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
    ELEVEN_TWO = 11.2

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


class Compression(CliFlag):
    NO = "u"
    YES = "c"


class DNGConverter:
    def __init__(self,
                 source,
                 dest=None,
                 compressed=Compression.YES,
                 camera_raw=CRawCompat.latest(),
                 dng_version=DNGVersion.latest(),
                 jpeg_preview=JPEGPreview.MEDIUM,
                 fast_load=False,
                 linear=False):
        self.prog_path = utils.locate_program("dngconverter")
        self.compressed = compressed.flag
        self.camera_raw = camera_raw.flag
        self.dng_version = dng_version.flag
        self.jpeg_preview = jpeg_preview.flag
        self.dest_path = dest
        self.linear = self.resolve_flag("l", linear)
        self.fast_load = self.resolve_flag("fl", fast_load)
        self.dest_path = self.resolve_flag(dest, dest, Path)

        if not self.prog_path:
            raise FileNotFoundError("DNGConverter is not installed!")
        self.source = utils.ensure_existing_dir(source)
        if not self.source:
            raise NotADirectoryError(
                f"{source} does not exists or is not a directory!")
        self.source = self.source.absolute()

    def resolve_flag(self, flag, value, on_true=None):
        if value:
            if on_true:
                return on_true(flag)
            return f"-{flag}"
        return ""

    @property
    def dest(self):
        if not self.dest_path:
            return ""
        return ("-d", str(self.dest_path.absolute()))

    @property
    def args(self):
        return [str(self.prog_path), self.compressed,
                self.camera_raw, self.dng_version,
                self.fast_load, self.linear, self.jpeg_preview,
                *self.dest]

    def convert(self):
        files = self.source.rglob("*.CR2")
        for p in files:
            print(f"Converting: {p.name} => {p.with_suffix('.dng').name}")
            self.convert_file(p)

    def convert_file(self, path):
        return subproc.run(self.args + [str(path)], stdout=subproc.DEVNULL,
                           stderr=subproc.DEVNULL)
