import numpy as np
import pytest
from hypothesis import given
from hypothesis import strategies as st

from pyforc.core import Coordinates, CoordinatesHcHb, CoordinatesHHr


@pytest.mark.parametrize(
    ("coord_str", "expected"),
    [
        ("hchb", CoordinatesHcHb),
        ("hhr", CoordinatesHHr),
    ],
)
def test_from_str(coord_str, expected):
    """Test that the right Coordinates subclass is returned for each string."""
    assert isinstance(Coordinates.from_str(coord_str), expected)


def test_from_str_invalid():
    """Test that an invalid name raises an error for Coordinates.from_str()."""
    name = "foo"
    with pytest.raises(ValueError, match=f"Invalid coordinate type {name}"):
        Coordinates.from_str(name)


@given(
    st.floats(min_value=-2 * 53 - 1, max_value=2 * 53 - 1),
    st.floats(min_value=-2 * 53 - 1, max_value=2 * 53 - 1),
)
def test_hchb_matrix(h, hr):
    """Test that the hchb coordinate matrix transforms coordinates as expected."""
    hhr_vec = np.array([h, hr, 0])

    coords = CoordinatesHcHb()
    assert coords.has_inverse

    arr = np.array(coords.get_matrix())

    [hc, hb, _] = arr @ hhr_vec

    assert np.isclose(h, hb + hc)
    assert np.isclose(hr, hb - hc)
    assert np.isclose(hc, (h - hr) / 2)
    assert np.isclose(hb, (h + hr) / 2)


@given(
    st.floats(min_value=-2 * 53 - 1, max_value=2 * 53 - 1),
    st.floats(min_value=-2 * 53 - 1, max_value=2 * 53 - 1),
)
def test_hhr_matrix(h, hr):
    """Test that the hhr coordinate matrix transforms coordinates as expected."""
    hhr_vec = np.array([h, hr, 0])

    coords = CoordinatesHHr()
    assert coords.has_inverse

    arr = np.array(coords.get_matrix())

    [h_calc, hr_calc, _] = arr @ hhr_vec

    assert h_calc == h
    assert hr_calc == hr
