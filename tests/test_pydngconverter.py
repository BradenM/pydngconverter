#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for pydngconverter package."""

from pathlib import Path

import pytest

import pydngconverter as pydng


@pytest.fixture
def mock_dng(mocker):
    """Mock DNG converter path"""
    mock_which = mocker.patch.object(pydng.main.utils.shutil, "which")
    mock_which.return_value = "/usr/bin/dngconverter"
    return "/usr/bin/dngconverter"


@pytest.fixture
def mock_rglob(mocker):
    """Mock raw file rglob search"""
    mock_val = (Path("/foo/one.CR2"), Path("/foo/two.CR2"))
    mock_rglob = mocker.patch.object(pydng.main.Path, 'rglob')
    mock_rglob.return_value = (Path("/foo/one.CR2"), Path("/foo/two.CR2"))
    return mock_val


@pytest.fixture
def mock_subproc(mocker):
    mock_subproc = mocker.patch.object(pydng.main.subproc, "run")
    return mock_subproc


def test_init(mocker, tmp_path):
    """Should fail if converter cannot be found"""
    mock_which = mocker.patch.object(pydng.main.utils.shutil, "which")
    mock_which.side_effect = [
        "/usr/bin/dngconverter", "",
        "/usr/bin/dngconverter", "/usr/bin/dngconverter"]
    pydng.DNGConverter(tmp_path)
    with pytest.raises(FileNotFoundError):
        pydng.DNGConverter(tmp_path)
    with pytest.raises(NotADirectoryError):
        pydng.DNGConverter((tmp_path / 'fake_path'))
    with pytest.raises(NotADirectoryError):
        tmp_file = tmp_path / 'text.txt'
        tmp_file.touch()
        pydng.DNGConverter(tmp_file)


def test_flag_resolve(mock_dng, tmp_path):
    dng = pydng.DNGConverter(tmp_path)
    mock_flag = True
    result = dng.resolve_flag("mf", mock_flag)
    assert result == "-mf"
    mock_flag = False
    result = dng.resolve_flag("mf", mock_flag)
    assert result == ""
    mock_flag = True
    result = dng.resolve_flag("mf", mock_flag, on_true=lambda x: "MOCK")
    assert result == "MOCK"


def test_destination(mock_dng, tmp_path):
    tmp_dest = tmp_path / 'dest'
    tmp_dest.mkdir()
    dng = pydng.DNGConverter(tmp_path)
    assert dng.dest == ("", "")
    dng = pydng.DNGConverter(tmp_path, dest=tmp_dest)
    assert dng.dest == ("-d", str(tmp_dest.absolute()))


def test_args(mock_dng, tmp_path):
    dng = pydng.DNGConverter(tmp_path,
                             jpeg_preview=pydng.JPEGPreview.FULL,
                             compressed=pydng.Compression.YES,
                             camera_raw=pydng.CRawCompat.ELEVEN_TWO,
                             dng_version=pydng.DNGVersion.ONE_FOUR,
                             fast_load=True, linear=True)
    expect_args = [mock_dng, "-c", "-cr11.2",
                   "-dng1.4", "-fl", "-l", "-p2"]
    assert sorted(dng.args) == sorted(expect_args)


def test_convert(mock_dng, mocker, tmp_path, mock_rglob, mock_subproc):
    dng = pydng.DNGConverter(tmp_path, multiprocess=False)
    dng.convert()
    expect_args = dng.args + ["", "", "/foo/two.CR2"]
    mock_subproc.assert_called_with(
        expect_args, stderr=mocker.ANY, stdout=mocker.ANY)


def test_multi_convert(mock_dng, mocker, tmp_path, mock_rglob, mock_subproc):
    mock_ray = mocker.patch.object(pydng.main, 'ray')
    mock_ray.wait.return_value = ([], [])
    mock_ray.is_initialized.return_value = False
    dng = pydng.DNGConverter(tmp_path, multiprocess=True)
    mock_ray.init.assert_called_once()
    list(dng.convert())
    mock_ray.remote.assert_called_with(dng.convert_file)
    # with extract thumbnail
    dng = pydng.DNGConverter(tmp_path, multiprocess=True,
                             jpeg_preview=pydng.JPEGPreview.EXTRACT)
    mock_ray.remote.assert_any_call(dng.extract_thumbnail)
    mock_ray.remote.assert_any_call(dng.convert_file)


def test_extract_thumbnail(mock_dng, mocker, tmp_path, mock_rglob,
                           mock_subproc):
    mock_image = mocker.patch.object(pydng.main, "Image")
    type(mock_subproc.return_value).stdout = mocker.PropertyMock(
        return_value=b"some binary image stuff")
    dng = pydng.DNGConverter(tmp_path,
                             multiprocess=False,
                             jpeg_preview=pydng.JPEGPreview.EXTRACT)
    dng.convert()
    mock_image.assert_called_with(blob=b"some binary image stuff")
    assert mock_image.call_count == 2
