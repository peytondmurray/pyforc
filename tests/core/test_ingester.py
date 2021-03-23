"""Tests for the ingesters."""
import numpy as np

from pyforc.core.ingester import interpolate


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

    h, hr, m, t = interpolate(h_raw, m_raw, t_raw)

    assert np.all(np.isnan(m[h < hr]))
    assert np.all(np.isnan(t))
