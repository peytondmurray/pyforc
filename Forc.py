import numpy as np
import pathlib
import errors


class Forc:

    def __init__(self, input):

        self.h = []               # Field
        self.hr = []              # Reversal field
        self.m = []               # Moment
        self.T = None               # Temperature (if any)
        self.drift_points = []    # Drift points

        self._from_file(input)

        return
    
    def _from_file(self, path):
        
        file = pathlib.Path(path)
        try:
            with open(file, 'r') as f:
                lines = f.readlines()
        except ...:
            print("Error opening specified data file: {}".format(file))
            raise

        raw_data = self._extract_raw_data(lines)

        return

    def _has_drift_points(self, lines):
        """Checks whether the measurement space has been specified in (Hc, Hb) coordinates or in (H, Hr). If it
        has been measured in (Hc, Hb) coordinates, the header will contain references to the limits of the
        measured data. If the measurement has been done in (Hc, Hb), drift points are necessary before the
        start of each reversal curve, which affects how the data is extracted.
        
        Parameters
        ----------
        lines : str
            Lines from a PMC-formatted data file.
        Returns
        -------
        bool
            True if 'Hb1' is detected in the start of a line somewhere in the data file, False otherwise.
        """

        for i in range(len(lines)):
            if "Hb1" == lines[i][:3]:
                return True
        return False

    def _has_temperature(self, line):
        """Checks for temperature measurements in a file. If line has 3 data values, the third is considered
        a temperature measurement.
        
        Parameters
        ----------
        line : str
            PMC formatted line to check
        Returns
        -------
        bool
            True if the line contains 3 floats or False if not.
        """

        return len(line.split(sep=',')) == 3

    def _extract_raw_data(self, lines):
        
        i = self._find_first_data_point(lines)
        if self._has_temperature(lines[i]):
            self._T = []

        if self._has_drift_points(lines):
            while i < len(lines):
                self._extract_drift_point(lines[i])
                i += 2
                i += self._extract_next_forc(lines[i:])
                i += 1
        else:
            while i < len(lines):
                i += self._extract_next_forc(lines[i:])
                self._extract_drift_point(lines[i-1:])
                i += 1

        return

    def _find_first_data_point(self, lines):
        """Return the index of the first data point in the PMC-formatted lines.
        
        Parameters
        ----------
        lines : str
            Contents of a PMC-formatted data file.
        Raises
        ------
        errors.DataFormatError
            If no lines begin with '+' or '-', an error is raised. Data points must begin with '+' or
        
        Returns
        -------
        int
            Index of the first data point. Skips over any header info at the start of the file, as long as
            the header lines do not begin with '+' or '-'.
        """

        for i in range(len(lines)):
            if lines[i][0] in ['+', '-']:
                return i
        
        raise errors.DataFormatError("No data found in file. Check data format spec.")

    def _extract_next_forc(self, lines):
        """Extract the next curve from the data.
        
        Parameters
        ----------
        lines : str
            Raw csv data in string format, from a PMC-type formatted file.
        Returns
        -------
        int
            Number of lines extracted
        """

        _h, _m, _hr, _T = [], [], [], []
        i = 0
        
        while lines[i][0] in ['+', '-']:
            split_line = lines[i].split(',')
            _h.append(float(split_line[0]))
            _hr.append(_h[0])
            _m.append(float(split_line[1]))
            if self.T is not None:
                _T.append(float(split_line[2]))
            i += 1

        self.h.append(_h)
        self.hr.append(_hr)
        self.m.append(_m)
        if self.T is not None:
            self.T.append(_T)
        
        return len(_h)

    def _extract_drift_point(self, line):
        """Extract the drift point from the specified input line. Only records the moment, 
        not the measurement field from the drift point (the field isn't used in any drift correction).
        Appends the drift point to self.drift_points.
        
        Parameters
        ----------
        line : str
            Line from data file which contains the drift point.
        """

        self.drift_points.append(float(line.split(sep=',')[-1]))
        return

