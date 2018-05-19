# Tests for PyFORC

import pytest
import sys
import main
import Forc
import numpy as np
# import matplotlib.pyplot as plt
# import matplotlib.cm as cm
# import matplotlib.collections as mc
import bokeh.plotting as bp
import bokeh.models.mappers as bmm
import bokeh.sampledata.iris as bsi
import bokeh.models as bm
import colorcet as cc


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
                        step=35,
                        drift=False)

    bp.output_file("test_fig.html")

    hmin, hmax = data.h_range()
    hrmin, hrmax = data.hr_range()

    ratio = (hmax-hmin)/(hrmax-hrmin)

    plot_size = 300

    plot = bp.figure(x_range=data.h_range(),
                     y_range=data.hr_range(),
                     match_aspect=True,
                     sizing_mode='fixed',
                     plot_width=int(plot_size*ratio),
                     plot_height=plot_size)

    color_mapper = bmm.LinearColorMapper(palette=cc.coolwarm,
                                         low=data.m_range()[0],
                                         high=data.m_range()[1],
                                         nan_color='white')

    plot.image(image=[data.m],
               color_mapper=color_mapper,
               dh=-1*np.diff(data.hr_range()),
               dw=-1*np.diff(data.h_range()),
               x=data.h_range()[0],
               y=data.hr_range()[0])

    bp.show(plot)

    return


if __name__ == '__main__':
    # test_gui()
    test_PMCForc_import()