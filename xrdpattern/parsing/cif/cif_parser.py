import numpy as np
from gemmi import cif
from numpy.typing import NDArray

from xrdpattern.xrd import PowderExperiment, XrdData, Metadata


class CifParser:
    def extract(self, fpath : str) -> XrdData:
        with open(fpath, 'r') as f:
            cif_content = f.read()
        experiment_info = PowderExperiment.from_cif(cif_content=cif_content)

        doc = cif.read_file(fpath)
        if len(doc) != 1:
            raise ValueError("Could not find pattern data in .cif located at {fpath}")
        block = doc.sole_block()
        x,y = self.extract_pattern_from_block(block)

        metadata = Metadata()
        lines = cif_content.split('\n')
        for l in lines:
            if '$Date' in l:
                parts = l.split()
                metadata.measurement_date = parts[1]

        pattern_data = XrdData(intensities=y, two_theta_values=x, powder_experiment=experiment_info, metadata=metadata)
        return pattern_data


    @staticmethod
    def extract_pattern_from_block(block) -> tuple[NDArray, NDArray]:
        x, y = None, None
        loops_gen = (i.loop for i in block if i.loop is not None)

        yfields = ["_pd_meas_counts_total", "_pd_meas_counts", "_pd_meas_intensity_total", "_pd_meas_intensity",
                   "_pd_proc_intensity_total", "_pd_proc_intensity_net"]
        for loop in loops_gen:
            if find_tags(yfields, loop.tags):
                for yf in yfields:
                    y = get_values_as_array(block, yf)
                    if y is not None:
                        y = np.array(y)
                        break

        loops_gen = (i.loop for i in block if i.loop is not None)
        xfields = ["_pd_proc_2theta_corrected", "_pd_meas_2theta_scan", "_pd_meas_2theta"]
        for loop in loops_gen:
            if find_tags(xfields, loop.tags):
                for xf in xfields:
                    x = get_values_as_array(block, xf)
                    if x is not None:
                        x = np.array(x)
                        break

        if x is None:
            rmin = block.find_value("_pd_meas_2theta_range_min")
            rmax = block.find_value("_pd_meas_2theta_range_max")

            if None in [rmin, rmax]:
                raise ValueError("Could not find 2theta range")
            rmin = cif.as_number(rmin)
            rmax = cif.as_number(rmax)
            x = np.linspace(rmin, rmax, len(y))

        if x is None or y is None:
            raise ValueError("Could not find 2theta or intensity values")

        return x,y

def find_tags(needles, haystack):
    for needle in needles:
        if needle in haystack:
            return True
    return False


def get_values_as_array(block, name, minlength = 2):
    column = block.find_values(name)
    if len(column) >= minlength:
        return list(map(cif.as_number, column))

    return None

if __name__ == "__main__":
    example_fpath = '/home/daniel/Drive/data/workspace/cod/1101016.cif'
    parser = CifParser()
    parser.extract(fpath=example_fpath)