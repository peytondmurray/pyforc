import numpy as np
import pathlib
import errors


class Forc:


    def __init__(self, input):


        return
    

    def _from_file(self, path):
        
        file = pathlib.Path(path)
        with open(file, 'r') as f:
            lines = f.readlines()

        raw_data = self._extract_raw_data(lines)

        return


    def _extract_raw_data(self, lines):
        
        data = []
        i = self._find_first_data_point(lines)
        while i < len(lines):
            self._extract_next_forc(lines, i)

        return data

    def _find_first_data_point(self, lines):
        
        for i in range(lines):
            if lines[i][0] in ['+', '-']:
                return i
        
        raise errors.DataFormatError("No data found in file.")

    def _extract_next_forc(self, lines, i):
        """Extract the next curve from the data.
        
        Parameters
        ----------
        lines : str
            Raw csv data in string format, from a PMC-type formatted file.
        i : int
            Index of first point in the curve to extract.
        Returns
        -------
        tuple of arrays
            (fields, moments)
        """

        
        

        h, m = [], []
        while lines[i][0] in ['+', '-']:
            split_line = lines[i].split(',')
            h.append(float(split_line[0]))
            m.append(float(split_line[1]))
            i += 1
        
        i += 1

        return h, m, i