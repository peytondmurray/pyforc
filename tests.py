# Tests for PyFORC

import pytest
import sys
import main
import Forc
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.collections as mc
import plotter



@pytest.mark.skip
def test_gui():
    sys.argv = ['main.py',
                'gui']
    main.parse_arguments()
    return


# @pytest.mark.skip
def test_Forc():
    Forc.PMCForc('./test_data/test_forc',
                 step=35,
                 drift=False)
    return


@pytest.mark.skip
def test_PMCForc_import():
    data = Forc.PMCForc('./test_data/test_forc',
                        step=100,
                        drift=False)

    data._extend_dataset(sf=3, method='flat')

    fig, axes = plt.subplots(nrows=1, ncols=2)
    axes[0].imshow(data.m,
                   extent=data.extent,
                   cmap='RdBu_r',
                   origin='lower')

    axes[0].plot(data.hr_range(), data.hr_range(), '-k')
    plotter.h_vs_m(axes[1], data, mask='outline', points='reversal')
    # plotter.h_hr_points(axes[0], data)
    plotter.hhr_space_h_vs_m(axes[0], data)

    plt.show()

    return

if __name__ == '__main__':
    # test_gui()
    test_PMCForc_import()
