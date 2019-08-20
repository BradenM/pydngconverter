#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for pydngconverter package."""

import pytest

import pydngconverter as pydng


def test_init(mocker, tmp_path):
    """Should fail if converter cannot be found"""
    mock_which = mocker.patch.object(pydng.main.utils.shutil, "which")
    mock_which.side_effect = [
        "/usr/bin/dngconverter", "", "/usr/bin/dngconverter", "/usr/bin/dngconverter"]
    pydng.DNGConverter(tmp_path)
    with pytest.raises(FileNotFoundError):
        pydng.DNGConverter(tmp_path)
    with pytest.raises(NotADirectoryError):
        pydng.DNGConverter((tmp_path / 'fake_path'))
    with pytest.raises(NotADirectoryError):
        tmp_file = tmp_path / 'text.txt'
        tmp_file.touch()
        pydng.DNGConverter(tmp_file)
