# Tests for PyFORC

import pytest
import sys
import main


def test_gui():
    sys.argv = ['main.py',
                'gui']
    main.parse_arguments()


if __name__ == '__main__':
    test_gui()
