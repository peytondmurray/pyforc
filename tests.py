# Tests for PyFORC

import pytest
import sys
import main
import Forc
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.collections as mc
import plotting



@pytest.mark.skip
def test_gui():
    sys.argv = ['main.py',
                'gui']
    main.parse_arguments()
    return


@pytest.mark.skip
def test_Forc():
    Forc.PMCForc('./test_data/test_forc',
                 step=35,
                 drift=False)
    return


@pytest.mark.skip
def PMCForc_import_and_plot():
    data = Forc.PMCForc('./test_data/test_forc',
                        step=100,
                        drift=False)

    data._extend_dataset(sf=3, method='flat')

    fig, axes = plt.subplots(nrows=1, ncols=2)
    plotting.m_hhr(axes[0], data)
    plotting.hhr_line(axes[0], data)
    plotting.h_vs_m(axes[1], data, mask='outline', points='reversal')
    plotting.hhr_space_h_vs_m(axes[0], data)

    plt.show()

    return


@pytest.mark.skip
def PMCForc_calculate_sg_FORC():
    data = Forc.PMCForc('./test_data/test_forc',
                        step=50,
                        drift=False)

    data.compute_forc_distribution(sf=3, method='savitzky-golay', extension='flat')

    fig, axes = plt.subplots(nrows=2, ncols=1)
    plotting.m_hhr(axes[0], data)
    plotting.rho_hhr(axes[1], data)

    plt.show()
    return


if __name__ == '__main__':
    # test_gui()
    # test_PMCForc_import()
    PMCForc_calculate_sg_FORC()