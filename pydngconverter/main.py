# -*- coding: utf-8 -*-

"""Main module."""

from pydngconverter import utils


class DNGConverter:
    def __init__(self, source, dest=None):
        self.prog_path = utils.locate_program("dngconverter")
        if not self.prog_path:
            raise FileNotFoundError("DNGConverter is not installed!")
        self.source = utils.ensure_existing_dir(source)
        if not self.source:
            raise NotADirectoryError(
                f"{source} does not exists or is not a directory!")
