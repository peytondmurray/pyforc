import numpy as np
import scipy.interpolate as si

from .config import Config
from .ingester import ForcData


def interpolate(
    data: ForcData,
    config: Config,
) -> ForcData:
    """Interpolate the raw dataset.

    m and t values for h < hr are set to np.nan.

    Parameters
    ----------
    step : float
        Step size along the h and hr directions to use for the interpolated dataset. Uses the
        same units given by the raw data. If None, the step will be determined from the median
        of the steps in the h-direction.
    interpolation : str
        Interpolation method to use; see docstring for scipy.interpolate.griddata for valid
        interpolation methods.

    Returns
    -------
    ForcData
        Interpolated dataset
    """
    if not config.step:
        step = data.get_step()
    else:
        step = config.step

    h_vals = np.concatenate(data.h_raw)
    hr_vals = np.concatenate(hr_vals_from_h(data.h_raw))
    m_vals = np.concatenate(data.m_raw)
    t_vals = np.concatenate(data.t_raw)

    h_min = np.min(h_vals)
    h_max = np.max(h_vals)
    hr_min = np.min(hr_vals)
    hr_max = np.max(hr_vals)

    h, hr = np.meshgrid(
        np.linspace(h_min, h_max, int((h_max - h_min) // step) + 1),
        np.linspace(hr_min, hr_max, int((hr_max - hr_min) // step) + 1),
    )

    hhr_vals = np.concatenate(
        (np.reshape(h_vals, (-1, 1)), np.reshape(hr_vals, (-1, 1))),
        axis=1
    ),

    m = si.griddata(hhr_vals, m_vals, (h, hr), method=config.interpolation)

    # Mask off the portion of the interpolated data that wasn't measured
    m[h < hr] = np.nan

    # If any temperature values are present in the raw data, interpolate over them; otherwise
    # all temperatures will be np.nan.
    if np.isnan(t_vals).any():
        t = np.full_like(m, fill_value=np.nan)
    else:
        t = si.griddata(hhr_vals, t_vals, (h, hr), method=config.interpolation)
        t[h < hr] = np.nan

    return ForcData.from_existing(
        data=data,
        h=h,
        hr=hr,
        m=m,
        t=t,
    )


def correct_drift(data: ForcData, _) -> ForcData:
    """
    Correct the raw magnetization for drift.

    If the measurement space is Hc/Hb, dedicated drift points must have been measured. If the
    measurement is H/Hr, the last datapoint along each curve is used. In either case, the points
    used for drift correction must have been measured above the saturation field.

    Parameters
    ----------
    data : ForcData
        Data for which drift correction is to be applied

    Returns
    -------
    ForcData
        Drift-corrected raw data; interpolated dataset is untouched.
    """
    m_raw = []
    mean_m_sat = np.mean(data.m_drift)
    for curve in data.m_raw:
        m_raw = curve - (curve[-1] - mean_m_sat)
    return ForcData.from_existing(
        data=data,
        m_raw=m_raw
    )


def hr_vals_from_h(h: list[np.ndarray]) -> list[np.ndarray]:
    """Generate an hr dataset from a ragged set of h curves.

    Parameters
    ----------
    h: list[np.ndarray]
        Ragged list of h-values for each reversal curve

    Returns
    -------
    list[np.ndarray]
        Ragged list of hr-values for each reversal curve. Each datapoint has an hr-value equal to
        the h-value of the first datapoint in the curve.
    """
    return [np.full_like(curve, fill_value=curve[0]) for curve in h]
