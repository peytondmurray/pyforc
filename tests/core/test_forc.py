"""Tests for the Forc classes."""
from pyforc.core import config, forc, ingester


def test_forc(raw_data_file: str):
    """Test that a Forc object can be instantiated from Hc/Hb data.

    Parameters
    ----------
    raw_data_file : str
        Raw data file to be imported.
    """
    f = forc.Forc(
        ingester.PMCIngester,
        config.Config(raw_data_file)
    )

    assert f
