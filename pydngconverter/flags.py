# -*- coding: utf-8 -*-

"""PyDNGConverter Flag Enums."""

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
