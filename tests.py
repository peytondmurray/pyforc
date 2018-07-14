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
import logging
import pickle

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s | %(filename)s:%(lineno)d | %(levelname)s: %(message)s')
# console_handler = logging.StreamHandler()
# console_handler.setFormatter(formatter)
# log.addHandler(console_handler)


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

    _, axes = plt.subplots(nrows=1, ncols=2)
    plotting.m_hhr(axes[0], data)
    plotting.hhr_line(axes[0], data)
    plotting.h_vs_m(axes[1], data, mask='h>hr', points='reversal')
    plotting.hhr_space_h_vs_m(axes[0], data)

    plt.show()

    return


@pytest.mark.skip
def PMCForc_calculate_sg_FORC():
    logging.info("Calculating savitzky-golay!")
    data = Forc.PMCForc('./test_data/test_forc', drift=False)

    data.compute_forc_distribution(sf=3, method='savitzky-golay', extension='flat')

    _, axes = plt.subplots(nrows=2, ncols=1)
    plotting.m_hhr(axes[0], data)
    plotting.rho_hhr(axes[1], data)

    plt.show()
    return


@pytest.mark.skip
def pickle_test():
    data = Forc.PMCForc('./test_data/test_forc', drift=False)
    with open('testpickle', 'wb') as f:
        pickle.dump(data, f)
    print('Pickle success!')
    return


def full_test():
    data = Forc.PMCForc('./test_data/test_forc', drift=False)
    data = data.slope_correction(h_sat=None, value=None)
    data = data.normalize()
    data = data.compute_forc_distribution(sf=3, method='savitzky-golay', extension='flat')
    return


if __name__ == '__main__':
    # test_gui()
    # test_PMCForc_import()
    # PMCForc_calculate_sg_FORC()
    full_test()
