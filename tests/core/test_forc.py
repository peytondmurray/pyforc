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


import pandas as pd
from preprocessing import preprocess

def test_preprocessor():
    """Check that the output config start time is the configured start time."""

    run_settings = json.loads("run_settings.json")
    preprocess(run_settings)
    df = pd.read_csv('w2_con.csv')
    assert df['TMSTRT'] == run_settings['start']
