"""Transformations which operate on ForcData objects."""
import numpy as np
import scipy.interpolate as si
import scipy.ndimage as sn
import scipy.optimize as so

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


def correct_drift(data: ForcData, config: Config) -> ForcData:
    """Correct the raw magnetization for drift.

    If the measurement space is Hc/Hb, dedicated drift points must have been measured. If the
    measurement is H/Hr, the last datapoint along each curve is used. In either case, the points
    used for drift correction must have been measured above the saturation field.

    Drift correction is carried out in the following steps:

        1. Calculate the average saturation magnetization, m_sat_avg
        2. Calculate a moving average of the saturation magnetization, m_sat_mov
        3. Use a cubic spline to interpolate between every nth point, m_sat_interp
        4. Subtract out the difference (m_sat_avg - m_sat_interp) from the magnetization of each
        curve

    Parameters
    ----------
    data : ForcData
        Data for which drift correction is to be applied

    Returns
    -------
    ForcData
        Drift-corrected raw data; interpolated dataset is untouched.
    """
    if len(data.m_drift) == 0:
        raise ValueError("No drift points in dataset.")

    m_sat_avg = np.mean(data.m_drift)

    kernel_size = 2 * config.drift_kernel_size + 1
    m_sat_mov = sn.convolve(
        data.m_drift,
        np.ones(kernel_size) / kernel_size,
        mode='nearest',
    )[::config.drift_density]
    index_mov = np.arange(0, len(data.m_drift), step=config.drift_density)

    m_sat_int = si.interp1d(index_mov, m_sat_mov, kind='cubic')

    return ForcData.from_existing(
        data=data,
        m_raw=[curve - (m_sat_int(i) - m_sat_avg) for i, curve in enumerate(data.m_raw)]
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


def normalize(data: ForcData, _) -> ForcData:
    """Normalize the magnetization to the range [-1, 1].

    Parameters
    ----------
    data : ForcData
        Data to normalize.

    Returns
    -------
    ForcData
        Normalized FORC data.
    """
    return ForcData.from_existing(
        data=data,
        m=1 - 2 * (data.m - np.nanmax(data.m)) / (np.nanmax(data.m) - np.nanmin(data.m))
    )


def correct_slope(data: ForcData, config: Config) -> ForcData:
    """Remove contributions to the magnetization which are linear in the field.

    This subtracts out para-/dia-magnetic background which is rarely of interest in magnetic
    systems.

    The fitting region is the region for which

        1. |h| > h_sat (the magnetic material is saturated)
        2. m is not NaN (ignore any NaNs introduced from interpolation)
        3. h > hr (ignore the unmeasurable region where Hc < 0)

    Parameters
    ----------
    data : ForcData
        Data for which the slope is to be corrected.
    config : Config
        Configuration containg the saturation magnetization `h_sat`, beyond which the slope is
        constant.

    Returns
    -------
    ForcData
        Data with the background subtracted out.
    """
    fit_region = (np.abs(data.h) > config.h_sat) & (~np.isnan(data.m)) & (data.h >= data.hr)

    h = data.h[fit_region].flatten()
    m = data.m[fit_region].flatten()

    (a, b), _ = so.curve_fit(line, h, m)

    return ForcData.from_existing(
        data=data,
        m=data.m - line(data.h, a, 0)
    )


def line(x: np.ndarray, a: float, b: float) -> np.ndarray:
    """Return y-values which are a linear function of x.

    Parameters
    ----------
    x : np.ndarray
        Abcissa
    a : float
        Slope of the line
    b : float
        y-intercept of the line

    Returns
    -------
    np.ndarray
        Ordinate
    """
    return a * x + b
