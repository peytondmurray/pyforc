import re

import numpy as np


class IngesterBase:

    def __init__(self, file_name, config):
        self.file_name = file_name
        self.config = config

        self.ingest(self.file_name)

        self.h_raw, self.m_raw, self.t_raw = [], [], []

    def ingest(self, file_name):
        raise NotImplementedError


class PMCIngester(IngesterBase):

    pattern = (
        r'(?P<h>[+-]\d*\.\d*),'
        r'(?P<m>[+-]\d*\.\d*)'
        r'(,(?P<t>[+-]\d*\.\d*))?'
    )

    def ingest(self, file_name):

        with open(file_name, 'r') as f:
            lines = f.readlines()

        # Find first data line
        i = 0
        while i < len(lines) and lines[i][0] not in '-+':
            i += 1

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
                self.h_raw.append(np.array(h_buf))
                self.m_raw.append(np.array(m_buf))
                self.t_raw.append(np.array(t_buf))
                h_buf, m_buf, t_buf = [], [], []

            i += 1

        return
