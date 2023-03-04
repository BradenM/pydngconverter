"""Compat module unit tests."""

import os
from pathlib import Path

import pytest
from pytest_mock import MockFixture

from pydngconverter import compat

platform_params = ["Linux", "Windows", "Darwin"]


@pytest.fixture(
    params=[
        pytest.param(
            p, marks=pytest.mark.skipif(compat.platform.system() != p, reason=f"{p} only.")
        )
        for p in platform_params
    ]
)
def mock_platform(request: pytest.FixtureRequest, mocker: MockFixture):
    return request.param


@pytest.fixture()
def platform_paths(mock_platform):
    map = {
        "Linux": (
            "/unix/path",
            r"Z:\unix\path",
        ),
        "Windows": (
            r"Z:\win\path",
            r"Z:\win\path",
        ),
        "Darwin": ("/unix/path", "/unix/path"),
    }
    return mock_platform, *map[mock_platform]


@pytest.fixture()
def platform_apps(mock_platform):
    map = {
        "Linux": "/usr/bin/ExampleApp",
        "Windows": r"C:\Program Files\ExampleApp.exe",
        "Darwin": "/Applications/ExampleApp.app/Contents/MacOS/ExampleApp",
    }
    return mock_platform, map[mock_platform]


@pytest.mark.asyncio()
async def test_get_compat_path(mocker: MockFixture, platform_paths):
    platform, in_path, expect_path = platform_paths
    mock_proc = mocker.AsyncMock()
    mock_proc.return_value.communicate.return_value = expect_path.encode(), ""
    mocker.patch.object(compat.asyncio, "create_subprocess_exec", mock_proc)
    ret_path = await compat.get_compat_path(in_path)
    assert ret_path == expect_path
    if platform == "Linux":
        mock_proc.assert_called_once()
    else:
        mock_proc.assert_not_called()


def test_resolve_executable(mocker: MockFixture, platform_apps):
    platform, expect_path = platform_apps
    mocker.patch("pydngconverter.compat.Path.exists", return_value=True)
    ret_path = compat.resolve_executable(["ExampleApp"])
    assert str(ret_path) == str(expect_path)


def test_resolve_executable_override(mocker):
    mocker.patch("pydngconverter.compat.Path.exists", return_value=True)
    os.environ["PYDNG_TEST_KEY"] = str(Path("/some/fake/path_exec"))
    assert Path(compat.resolve_executable(["path_exec"], env_override="PYDNG_TEST_KEY")) == Path(
        "/some/fake/path_exec"
    )


def test_platform_enum(mock_platform):
    if mock_platform == "Windows":
        assert compat.Platform.get().is_win
    if mock_platform == "Linux":
        assert compat.Platform.get().is_nix
    if mock_platform == "Darwin":
        assert compat.Platform.get().is_darwin
