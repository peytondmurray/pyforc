# Tests for PyFORC

import pytest
import sys
import main


def test_cmd():
    sys.argv = ['main.py',
                'gui']
    main.cmd_line()


if __name__ == '__main__':
    test_cmd()
