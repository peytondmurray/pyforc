"""Classes for storing, extracting, and processing FORC data."""
from typing import Type

from .config import Config
from .ingester import IngesterBase


class Forc():
    """
    Generic for storing, extracting, and processing FORC data.

    Parameters
    ----------
    ingester: Ingester
        Ingester class to use to ingest the raw data
    config: Config
        Config instance holding the ingester configuration details
    """

    def __init__(self, ingester: Type[IngesterBase], config: Config):
        self.config = config
        self.ingester = ingester(self.config)
        self.data = self.ingester.ingest(self.config)
