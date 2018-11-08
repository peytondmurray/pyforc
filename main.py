import pathlib
import argparse
import logging
import sys
import logging
import PyQt5
import PyFORCGUI

# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s | %(filename)s:%(lineno)d | %(levelname)s: %(message)s')


def parse_arguments():
    """Instantiate the argument parser and run the appropriate code, depending on whether the user wants to
    start the gui or load a script.
    
    """

    parser = generate_parser()
    args = vars(parser.parse_args())

    logging.info('mode = {}'.format(args['mode']))

    if args['mode'] == 'gui':
        start_gui()
    elif args['mode'] == 'run':
        run()
    elif args['mode'] == 'load':
        load()
    else:
        parser.print_usage()
        sys.exit(0)

    return


def generate_parser():
    """Generate an argument parser for CLI arguments.

    Returns
    -------
    argparse.ArgumentParser
        Parses the arguments. See argparse.ArgumentParser for additional info.
    """

    parser = argparse.ArgumentParser(description="Compute FORC distributions.")
    subparsers = parser.add_subparsers(title='Mode',
                                       dest='mode',
                                       description='Specify which operation to perform.')

    subparsers.add_parser('gui',
                          help="Launch the gui")
    parser_run = subparsers.add_parser('run',
                                       help="Process a dataset and generate a FORC distribution.")
    parser_run.add_argument('-F', '--file',
                            type=str,
                            required=True,
                            metavar='FILE',
                            dest='data_file',
                            help='Specify input data file')

    parser_load = subparsers.add_parser('load')
    parser_load.add_argument('-F', '--file',
                             type=str,
                             required=True,
                             metavar='FILE',
                             dest='load_file',
                             help='Specify processed FORC data file')

    return parser


def load():
    raise NotImplementedError('Support for loading a script file not yet implemented.')


def run():
    raise NotImplementedError


def start_gui():
    """Begin the PyQt5-based GUI.
    
    """

    app = PyQt5.QtWidgets.QApplication(sys.argv)
    win = PyFORCGUI.PyFORCGUI(app)
    win.setWindowTitle("PyFORC")
    win.show()
    sys.exit(app.exec_())
    return


if __name__ == '__main__':
    # parse_arguments()
    start_gui()  # For now, only the GUI is supported.
