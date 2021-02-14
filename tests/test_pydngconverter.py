# -*- coding: utf-8 -*-

"""PyDNGConverter tests."""
from pathlib import Path

from pytest_mock import MockFixture

import pydngconverter as pydng
from pydngconverter import flags
import pytest

ARG_SCENARIOS = [
    # no thumbnail.
    dict(jpeg_preview=flags.JPEGPreview.NONE),
    # use dng converter
    dict(jpeg_preview=flags.JPEGPreview.MEDIUM),
    # extract
    dict(jpeg_preview=flags.JPEGPreview.EXTRACT),
]


@pytest.fixture
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
