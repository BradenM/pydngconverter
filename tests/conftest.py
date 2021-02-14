# -*- coding: utf-8 -*-

"""PyDNGConverter test config."""

import pytest
from pytest_mock import MockFixture


@pytest.fixture(autouse=True, scope="session")
def mock_wand(session_mocker: MockFixture):
    session_mocker.patch("pydngconverter.main.Image")
