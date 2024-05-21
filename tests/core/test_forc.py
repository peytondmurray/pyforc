"""Tests for the Forc classes."""

import pyforc.core as pfc


def test_forc(raw_data_file):
    """Test that a Forc object can be instantiated from Hc/Hb data.

    Parameters
    ----------
    raw_data_file : str
        Raw data file to be imported.
    """
    f = pfc.forc.Forc(
        pfc.ingester.PMCIngester,
        pfc.config.Config(
            file_name=raw_data_file,
            pipeline=[
                pfc.ops.correct_drift,
                pfc.ops.interpolate,
            ],
        ),
    )

    assert f
