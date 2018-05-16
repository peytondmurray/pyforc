# Tests for PyFORC

import pytest
import sys
import main
import Forc


@pytest.mark.skip
def test_gui():
    sys.argv = ['main.py',
                'gui']
    main.parse_arguments()
    return


def test_Forc():
    Forc.PMCForc('./test_data/test_forc')
    return


if __name__ == '__main__':
    test_gui()
