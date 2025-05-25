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
        data = self.ingest()
        return functools.reduce(
            lambda x, f: f(x, self.config),
            self.config.pipeline,
            data,
        )


class PMCIngester(IngesterBase):
    """Ingester for data measured by Princeton Measurements Corporation (now Lakeshore) VSMs."""

    pattern = (
        r"(?P<h>([+-]\d+\.\d+(E[+-]\d+)?)),"
        r"(?P<m>([+-]\d+\.\d+(E[+-]\d+)?))"
        r"(,(?P<t>([+-]\d+\.\d+(E[+-]\d+)?)))?"
    )

    def ingest(self) -> ForcData:
        """Ingest the raw data from the data file.

        Returns
        -------
        ForcData
            Raw field (h), magnetization (m), and temperature (t) (if present) values.
        """
        if not self.config.file_name:
            raise ValueError("No file name specified.")

        with open(self.config.file_name) as f:
            lines = f.readlines()

        # Find first data line
        i = 0
        while i < len(lines) and lines[i][0] not in "-+":
            i += 1

        header = lines[:i]

        if self.is_hhr(header):
            return self.ingest_from_hhr(lines, i)
        return self.ingest_from_hchb(lines, i)

    def ingest_curve(self, lines: list[str], i: int) -> tuple[np.ndarray, ...]:
        """Ingest a single reversal curve.

        Parameters
        ----------
        lines : list[str]
            Lines from the raw data file
        i : int
            Line number where the curve to be ingested starts

        Returns
        -------
        tuple[np.ndarray, ...]
            (h, m, t) arrays for the ingested curve
        """
        h_buf, m_buf, t_buf = [], [], []
        j = i

        while j < len(lines):
            match = re.search(self.pattern, lines[j])

            if match:
                groups = match.groupdict()
                h_buf.append(float(groups["h"]))
                m_buf.append(float(groups["m"]))
                t_buf.append(float(groups["t"]) if groups["t"] else np.nan)

            else:
                # End of the reversal curve
                return np.array(h_buf), np.array(m_buf), np.array(t_buf)

            j += 1

        return np.array(h_buf), np.array(m_buf), np.array(t_buf)

    def ingest_from_hchb(self, lines: list[str], i: int) -> ForcData:
        """Ingest the PMC file assuming an hc/hb measurement space.

        Parameters
        ----------
        lines : list[str]
            Lines from the raw data file
        i : int
            Line number corresponding to the first curve

        Returns
        -------
        ForcData
            Raw FORC data
        """
        m_drift = []
        h_raw, m_raw, t_raw = [], [], []
        while i < len(lines):
            match = re.search(self.pattern, lines[i])
            if match:
                # Handle drift point
                groups = match.groupdict()
                m_drift.append(float(groups["m"]))

                # Next line should be blank; line after is the start of the reversal curve data
                if re.search(self.pattern, lines[i + 1]) or not re.search(
                    self.pattern, lines[i + 2]
                ):
                    raise ValueError(f"Unexpected data format starting on line {i}")

                i += 2
                h_buf, m_buf, t_buf = self.ingest_curve(lines, i)
                if h_buf.size > 0:
                    i += len(h_buf)
                    h_raw.append(h_buf)
                    m_raw.append(m_buf)
                    t_raw.append(t_buf)

            i += 1

        return ForcData(
            h_raw=h_raw,
            m_raw=m_raw,
            t_raw=t_raw,
            m_drift=np.array(m_drift),
        )

    def ingest_from_hhr(self, lines: list[str], i: int):
        """Ingest the PMC file assuming an h/hr measurement space.

        Parameters
        ----------
        lines : list[str]
            Lines from the raw data file
        i : int
            Line number corresponding to the first curve

        Returns
        -------
        ForcData
            Raw FORC data
        """
        m_drift = []
        h_raw, m_raw, t_raw = [], [], []
        while i < len(lines):
            match = re.search(self.pattern, lines[i])
            if match:
                # Line contains data; append to buffers and continue
                h_buf, m_buf, t_buf = self.ingest_curve(lines, i)
                if h_buf.size > 0:
                    i += len(h_buf)
                    h_raw.append(h_buf)
                    m_raw.append(m_buf)
                    t_raw.append(t_buf)

                    # Last point in the curve is used as drift point
                    m_drift.append(m_buf[-1])

            i += 1

        return ForcData(
            h_raw=h_raw,
            m_raw=m_raw,
            t_raw=t_raw,
            m_drift=np.array(m_drift),
        )

    @staticmethod
    def is_hhr(header: list[str]) -> bool:
        """Check whether the header comes from a file measured in h/hr space.

        Parameters
        ----------
        header : list[str]
            Header lines for a PMC file

        Returns
        -------
        bool
            True if the header comes from a file measured across h/hr space, False otherwise.
        """
        return not any(re.match("(Hc1|Hc2|Hb1|Hb2).*", line) for line in header)
