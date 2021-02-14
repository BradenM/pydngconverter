# -*- coding: utf-8 -*-

"""Compat module unit tests."""

import pytest
from pytest_mock import MockFixture

from pydngconverter import compat

platform_params = ["Linux", "Windows", "Darwin"]

@pytest.fixture(params=platform_params)
def mock_platform(request: pytest.FixtureRequest, mocker: MockFixture):
    mocker.patch.object(compat.platform, 'system', return_value=request.param)
    return request.param

@pytest.fixture
def platform_paths(mock_platform):
    map = {
        'Linux': ('/unix/path', r'Z:\\unix\\path',),
        'Windows': (r'Z:\\win\\path', r'Z:\\win\\path', ),
        'Darwin': ('/unix/path', '/unix/path'),
    }
    return mock_platform, *map[mock_platform]


@pytest.mark.asyncio
async def test_get_compat_path(mocker: MockFixture, platform_paths):
    platform, in_path, expect_path = platform_paths
    mock_proc = mocker.AsyncMock()
    mock_proc.return_value.communicate.return_value = expect_path.encode(), ""
    mocker.patch.object(compat.asyncio, 'create_subprocess_exec', mock_proc)
    ret_path = await compat.get_compat_path(in_path)
    assert ret_path == expect_path
    if platform == 'Linux':
        mock_proc.assert_called_once()
    else:
        mock_proc.assert_not_called()
