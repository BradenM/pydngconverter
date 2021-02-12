# -*- coding: utf-8 -*-

"""Compat module unit tests."""

import pytest
from pydngconverter import compat
from pytest_mock import MockFixture


@pytest.mark.parametrize(
    'platform,in_path,expect_path',
    [
        ('Linux', '/unix/path', r'Z:\\unix\\path',),
        ('Windows', r'Z:\\win\\path', r'Z:\\win\\path', ),
        ('Darwin', '/unix/path', '/unix/path'),
    ]
)
def test_get_compat_path(mocker: MockFixture, platform, in_path, expect_path):
    mocker.patch.object(compat.platform, 'system', return_value=platform)
    mock_proc = mocker.MagicMock()
    mock_proc.return_value.stdout = expect_path
    mocker.patch.object(compat.subp, 'run', mock_proc)
    ret_path = compat.get_compat_path(in_path)
    assert ret_path == expect_path
    if platform == 'Linux':
        mock_proc.assert_called_once()
    else:
        mock_proc.assert_not_called()
