"""PyDNGConverter tests."""
from __future__ import annotations

from pathlib import Path

import pytest
from pytest_mock import MockFixture
from typing_extensions import NamedTuple

import pydngconverter as pydng
from pydngconverter import flags
from pydngconverter.dngconverter import DNGParameters

ARG_SCENARIOS = [
    # no thumbnail.
    dict(jpeg_preview=flags.JPEGPreview.NONE),
    # use dng converter
    dict(jpeg_preview=flags.JPEGPreview.MEDIUM),
    # extract
    dict(jpeg_preview=flags.JPEGPreview.EXTRACT),
]


@pytest.fixture()
def with_mock_source(tmp_path):
    root_p = tmp_path / "mocksource"
    root_p.mkdir(exist_ok=True)
    for i in range(4):
        file = root_p / f"mockfile{i}.cr2"
        file.touch(exist_ok=True)
    return root_p


@pytest.fixture(params=ARG_SCENARIOS)
def with_scenarios(request, with_mock_source):
    return (with_mock_source,), dict(**request.param)


def test_init_setup(with_scenarios, mocker: MockFixture):
    mock_resolve = mocker.patch("pydngconverter.compat.resolve_executable")
    mock_resolve.return_value = Path(""), ""
    dng = pydng.DNGConverter(*with_scenarios[0], **with_scenarios[-1])
    dng_call = mocker.call(["Adobe DNG Converter", "dngconverter"], "PYDNG_DNG_CONVERTER")
    exif_call = mocker.call(["exiftool"], "PYDNG_EXIF_TOOL")
    if dng.parameters.jpeg_preview == flags.JPEGPreview.NONE:
        mock_resolve.assert_has_calls([dng_call])
        mock_resolve.assert_called_once()
    if dng.parameters.jpeg_preview == flags.JPEGPreview.MEDIUM:
        mock_resolve.assert_has_calls([dng_call])
        mock_resolve.assert_called_once()
    if dng.parameters.jpeg_preview == flags.JPEGPreview.EXTRACT:
        mock_resolve.assert_has_calls([dng_call, exif_call])
        assert mock_resolve.call_count == 2


default_args = ["-c", "-cr14.0", "-dng1.6", "-p1"]


class DNGParamCase(NamedTuple):
    params: DNGParameters
    expect_args: list[str]


ParameterCases = [
    DNGParamCase(DNGParameters(), default_args),
    # no compression
    DNGParamCase(
        params=DNGParameters(
            compression=flags.Compression.NO,
        ),
        expect_args=["-u", *default_args[1:]],
    ),
    # fastload
    DNGParamCase(
        params=DNGParameters(fast_load=True),
        expect_args=[*default_args[:-1], "-fl", "-p1"],
    ),
    # linear dng
    DNGParamCase(
        params=DNGParameters(linear=True),
        expect_args=[*default_args[:-1], "-l", "-p1"],
    ),
    # implied lossy side only
    DNGParamCase(
        params=DNGParameters(side=1),
        expect_args=[*default_args[:-1], "-side", "1", "-p1"],
    ),
    # implied lossy count only
    DNGParamCase(
        params=DNGParameters(count=1),
        expect_args=[*default_args[:-1], "-count", "1", "-p1"],
    ),
    # implied lossy side/count
    DNGParamCase(
        params=DNGParameters(side=1, count=1),
        expect_args=[*default_args[:-1], "-side", "1", "-count", "1", "-p1"],
    ),
    # explicit lossy side/count
    DNGParamCase(
        params=DNGParameters(side=1, count=1, lossy=flags.LossyCompression.NO),
        expect_args=[*default_args[:-1], "-side", "1", "-count", "1", "-p1"],
    ),
    # dng converter jpeg
    DNGParamCase(
        params=DNGParameters(jpeg_preview=flags.JPEGPreview.FULL),
        expect_args=[*default_args[:-1], "-p2"],
    ),
    # none jpeg
    DNGParamCase(
        params=DNGParameters(jpeg_preview=flags.JPEGPreview.NONE),
        expect_args=[*default_args[:-1], "-p0"],
    ),
    # pydngconverter exif extract jpeg
    DNGParamCase(
        params=DNGParameters(jpeg_preview=flags.JPEGPreview.NONE),
        expect_args=[*default_args[:-1], "-p0"],
    ),
]


@pytest.mark.parametrize("case", ParameterCases)
def test_dng_parameters_args(case: DNGParamCase):
    assert list(case.params.iter_args) == case.expect_args
