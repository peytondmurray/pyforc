import pathlib
import errors
import argparse
import logging
import sys
import logging
import PyQt5

log = logging.getLogger(__name__)


def cmd_line():
    parse_arguments()
    return


def parse_arguments():
    parser = generate_parser()
    args = vars(parser.parse_args())

    log.info('mode = {}'.format(args['mode']))

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
    pass


def run():
    pass


def start_gui():

    return


if __name__ == '__main__':
    cmd_line()
