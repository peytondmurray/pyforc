import numpy as np

from . import ingest


class Forc():
    """
    Class for storing, extracting, and processing FORC data.
    """

    def __init__(self, file_name, ingester, config):
        self.file_name = file_name
        self.config = config
        self.ingester = ingester(self.file_name, self.config)


    def get_data(self):
        return self.data

    def get_config(self):
        return self.config

    def get_file_name(self):
        return self.file_name
