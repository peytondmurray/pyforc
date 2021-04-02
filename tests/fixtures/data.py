"""Test fixtures of real data."""
import pathlib

import pytest


@pytest.fixture()
def raw_data_file():
    """Path to a PMC hc/hb data file."""
    return pathlib.Path(__file__).parent / 'hchb_forc'
