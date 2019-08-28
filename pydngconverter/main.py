# -*- coding: utf-8 -*-

"""
pydngconverter.main
====================================
PyDNGConverter Code Module
"""

import subprocess as subproc
from enum import Enum
from pathlib import Path

import ray
from wand.image import Image

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
    EXTRACT = 3

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
    """Python Interface to Adobe DNG Converter

    Takes the same parameters as the Adobe DNG Converter, but uses
    enums and such to make it easier to use.

    Args:
        source (os.Pathlike): Path to source directory containing raw files
        dest (os.Pathlike, optional): Path to destination.
            Defaults to source directory.
        compressed (Compression, optional): Enable DNG Compression.
            Defaults to Compression.YES.
        camera_raw (CRawCompat, optional): Set Camera Raw Compat vers.
             Defaults to CRawCompat.latest().
        dng_version (DNGVersion, optional): Set DNG Backwards Compat vers.
             Defaults to DNGVersion.latest().
        jpeg_preview (JPEGPreview, optional): JPEG Preview size.
             Defaults to JPEGPreview.MEDIUM.
        fast_load (bool, optional): Embed fast load data (for jpeg preview).
             Defaults to False.
        linear (bool, optional): Output linear DNG files.
             Defaults to False.
        multiprocess (bool, optional): Convert multiple files at once.
             Defaults to True.
        ray_args (dict, optional): Additonal args to pass to ray.
             Defaults to {}.

    Raises:
        FileNotFoundError: DNG Converter cannot be found.
        NotADirectoryError: Source directory does not exist
             or is not a directory.
    """

    def __init__(self,
                 source,
                 dest=None,
                 compressed=Compression.YES,
                 camera_raw=CRawCompat.latest(),
                 dng_version=DNGVersion.latest(),
                 jpeg_preview=JPEGPreview.MEDIUM,
                 fast_load=False,
                 linear=False,
                 multiprocess=True,
                 ray_args={}):
        self.prog_path = self.resolve_binary("dngconverter")
        self.compressed = compressed.flag
        self.camera_raw = camera_raw.flag
        self.dng_version = dng_version.flag
        self.jpeg_preview = jpeg_preview
        self.dest_path = dest
        self.linear = self.resolve_flag("l", linear)
        self.fast_load = self.resolve_flag("fl", fast_load)
        self.dest_path = self.resolve_flag(dest, dest, Path)
        self.multiprocess = multiprocess

        if self.multiprocess and not ray.is_initialized():
            ray.init(**ray_args)

        if self.jpeg_preview == JPEGPreview.EXTRACT:
            self.exif_path = self.resolve_binary("exiftool")

        self.source = utils.ensure_existing_dir(source)
        if not self.source:
            raise NotADirectoryError(
                f"{source} does not exists or is not a directory!")
        self.source = self.source.absolute()

    def resolve_binary(self, binary_name):
        """Resolves path to binary executable

        Args:
            binary_name (str): Executable name

        Raises:
            FileNotFoundError: Raised when binary is not found

        Returns:
            os.Pathlike: Path to binary
        """
        path = utils.locate_program(binary_name)
        if not path:
            raise FileNotFoundError(f"{binary_name} is not installed!")
        return path

    def resolve_flag(self, flag, value, on_true=None):
        """Resolves boolean or special flags

        Args:
            flag (str): Flag that DNGConverter takes.
            value (any): Value used to resolve.
            on_true (callable, optional): Alternative callback on true.
                 Defaults to None.

        Returns:
            str: Resolved flag as string.
        """
        if value:
            if on_true:
                return on_true(flag)
            return f"-{flag}"
        return ""

    @property
    def dest(self):
        """Destination flag property

        Returns:
            tuple: Tuple containing flag and destination
        """
        if not self.dest_path:
            return ("", "")
        return ("-d", str(self.dest_path.absolute()))

    @property
    def args(self):
        """Args that will be passed to DNGConverter

        Returns:
            list: List of args to pass
        """
        _args = [str(self.prog_path), self.compressed,
                 self.camera_raw, self.dng_version,
                 self.fast_load, self.linear]
        if self.jpeg_preview != JPEGPreview.EXTRACT:
            _args.append(self.jpeg_preview.flag)
        return _args

    def convert_multiproc(self, raw_files):
        """Convert with multiprocessing.

        Args:
            raw_files ([os.Pathlike]): Paths to raw files

        Returns:
            tuple: List of DNG paths,
                List of thumbnail paths if JPEGPreview.EXTRACT is passed.
                Defaults to None
        """
        rem_extract_thumb = ray.remote(DNGConverter.extract_thumbnail)
        rem_convert_path = ray.remote(DNGConverter.convert_file)
        raw_files = [str(p) for p in raw_files]
        img_ids = [ray.put(i) for i in raw_files]
        thumbs = None
        if self.jpeg_preview == JPEGPreview.EXTRACT:
            thumbs = ray.get([rem_extract_thumb.remote(
                i, self.dest, self.exif_path) for i in img_ids])
        converted = ray.get([rem_convert_path.remote(
            i, self.dest, self.args) for i in img_ids])
        return (converted, thumbs)

    def convert(self):
        """Convert all files in source directory"""
        files = self.source.rglob("*.CR2")
        _, dest_path = self.dest
        Path(dest_path).mkdir(exist_ok=True)
        if self.multiprocess:
            return self.convert_multiproc(files)
        thumbs = None
        if self.jpeg_preview == JPEGPreview.EXTRACT:
            thumbs = [self.extract_thumbnail(
                p, self.dest, self.exif_path) for p in files]
        converted = [self.convert_file(
            str(p), self.dest, self.args) for p in files]
        return (converted, thumbs)

    @staticmethod
    def extract_thumbnail(path, dest, exif_path=None):
        """Extract thumbnail from exif data

        Args:
            path (str): path to raw file
            dest (str): path to save thumbnail
            exif_path (str): Path to exiftool

        Returns:
            str: thumbnail path
        """
        if not path:
            return
        exif_path = exif_path or "exiftool"
        args = f"{exif_path} -b -previewImage".split()
        thumb_bytes = subproc.run([*args, path], stdout=subproc.PIPE).stdout
        out_name = Path(path).with_suffix('.thumb.jpg').name
        out_path = Path(dest[1]) / out_name
        print(f"Extracting Thumbnail: {out_name}")
        with Image(blob=thumb_bytes) as img:
            img.resize(int(img.width*.10), int(img.height*.10))
            img.rotate(270)
            img.save(filename=str(out_path))
        return str(out_path)

    @staticmethod
    def convert_file(path, dest, dng_args):
        """Converts a single file to .DNG"

        Args:
            path (os.Pathlike): Path to file.
            dest (tuple): Destination flag and path.
            dng_args ([str]): Additional args to pass to DNG Converter.

        Returns:
           str: Path to DNG file
        """
        if not path:
            return
        suffix = path.split('.')[-1]
        dest_file = path.replace(f".{suffix}", ".dng")
        d_flag, d_parent = dest
        dng_args.extend([*dest, str(path)])
        print(f"Converting: {path} => {dest_file}")
        subproc.run(dng_args, stdout=subproc.DEVNULL,
                    stderr=subproc.DEVNULL)
        return dest_file
