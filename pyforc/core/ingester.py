"""Classes for ingesting FORC data."""

import functools
import re

import numpy as np

from .config import Config
from .forcdata import ForcData


class IngesterBase:
    """Base class for all ingester types.

    Ingesters are responsible for reading the raw data and generating a ForcData instance containing
    raw and interpolated datasets.

    Parameters
    ----------
    config : Config
        Ingester configuration to use for ingesting the raw data.
    pipeline: List[Callable]
        Ingestion pipeline to run
    """

    def __init__(self, config: Config):
        self.config = config

    def ingest(self) -> ForcData:
        """Ingest the raw data.

        Returns
        -------
        ForcData
            Raw field (h), magnetization (m), and temperature (t) (if present) values. No
            interpolation is carried out by default.
        """
        raise NotImplementedError

    def run(self):
        """Run the ingestion pipeline.

        This function chains together the pipeline, feeding the output of each function in the
        pipeline into the input of the next.

        Retuns
        ------
        ForcData
            Interpolated dataset
        """
        return functools.reduce(
            lambda x, f: f(x, self.config),
            self.config.pipeline,
            self.ingest()
        )


class PMCIngester(IngesterBase):
    """Ingester for data measured by Princeton Measurements Corporation (now Lakeshore) VSMs."""

    pattern = (
        r'(?P<h>([+-]\d+\.\d+(E[+-]\d+)?)),'
        r'(?P<m>([+-]\d+\.\d+(E[+-]\d+)?))'
        r'(,(?P<t>([+-]\d+\.\d+(E[+-]\d+)?)))?'
    )

    def ingest(self) -> ForcData:
        """Ingest the raw data.

        Returns
        -------
        ForcData
            Raw field (h), magnetization (m), and temperature (t) (if present) values. No
            interpolation is carried out by default.
        """
        with open(self.config.file_name, 'r') as f:
            lines = f.readlines()

        # Find first data line
        i = 0
        while i < len(lines) and lines[i][0] not in '-+':
            i += 1

        data = ForcData()

        # Read the data in line by line
        h_buf, m_buf, t_buf = [], [], []
        while i < len(lines):
            match = re.search(self.pattern, lines[i])
            if match:
                # Line contains data; append to buffers and continue
                groups = match.groupdict()
                h_buf.append(float(groups['h']))
                m_buf.append(float(groups['m']))
                t_buf.append(float(groups['t']) if groups['t'] else np.nan)

            elif h_buf and m_buf:
                # This is the end of a reversal curve; append buffers to raw data
                data.h_raw.append(np.array(h_buf))
                data.m_raw.append(np.array(m_buf))
                data.t_raw.append(np.array(t_buf))
                h_buf, m_buf, t_buf = [], [], []

            i += 1

        return data
