

import pathlib
import errors
import argparse
import logging

logging.getLogger(__name__)


def cmd_line():
    generate_parser()
    return


def generate_parser():

    parser = argparse.ArgumentParser(description="Compute FORC distributions.")
    subparsers = parser.add_subparsers(title="Mode",
                                       dest='mode',
                                       description='Specify which operation to perform.')

    parser_run = subparsers.add_parser("run",
                                       help="Process a dataset and generate a FORC distribution.")
    parser_run.add_argument('-F', '--file',
                            type=str,
                            required=True,
                            metavar='FILE',
                            dest='data_file',
                            help='Specify input data file')


if __name__ == '__main__':
    cmd_line()
