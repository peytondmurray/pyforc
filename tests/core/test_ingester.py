"""Tests for the ingesters."""
import numpy as np

from pyforc.core.config import Config
from pyforc.core.forcdata import ForcData
from pyforc.core.ops import interpolate


def test_interpolate():
    """Test that interpolate masks m[h<hr] and avoids interpolating t if t_raw is empty."""
    h_raw = [
        np.array([1, 2, 3]),
        np.array([0, 1, 2, 3]),
        np.array([-1, 0, 1, 2, 3]),
    ]

    m_raw = [
        np.array([1, 2, 3]),
        np.array([0, 1, 2, 3]),
        np.array([-1, 0, 1, 2, 3]),
    ]

    t_raw = [
        np.array([np.nan, np.nan, np.nan]),
        np.array([np.nan, np.nan, np.nan, np.nan]),
        np.array([np.nan, np.nan, np.nan, np.nan, np.nan]),
    ]

    data = interpolate(
        ForcData(h_raw=h_raw, m_raw=m_raw, t_raw=t_raw),
        config=Config(file_name=None),
    )

    assert np.all(np.isnan(data.m[data.h < data.hr]))
    assert np.all(np.isnan(data.t))
