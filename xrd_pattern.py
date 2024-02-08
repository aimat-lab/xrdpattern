from typing import Optional
from numpy import ndarray as NumpyArr
from xylib.xyconv import convert_file


class XrdPattern:
    def __init__(self, filepath : Optional[str] = None):
        self.wave_length_angstrom : Optional[float] = None
        self.np_degree_repr : Optional[NumpyArr] = None
        self.source_file : Optional[bytes] = None

        if filepath:
            self.import_from_file(filepath=filepath)

    def import_from_file(self,filepath : str):
        convert_file()


    def export_to_file(self):
        pass


    def get_wavelength_angstrom(self) -> float:
        return self.wave_length_angstrom


    def get_standardized(self):
        pass

    def get_np_repr(self):
        if not self.np_degree_repr:
            raise ValueError(f"Numpy array is None")

        return self.np_degree_repr

xyconv.convert_file()