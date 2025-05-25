"""Classes for storing, extracting, and processing FORC data."""

from .config import Config
from .ingester import IngesterBase


class Forc:
    """Generic container for extracting and processing FORC data.

    Parameters
    ----------
    ingester: Ingester
        Ingester class to use to ingest the raw data
    config: Config
        Config instance holding the ingester configuration details
    """

    def __init__(self, ingester: type[IngesterBase], config: Config):
        self.config = config
        self.ingester = ingester(self.config)
        self.data = self.ingester.run()
