import os

from dataclasses import dataclass
from xrdpattern.pattern import XrdPattern
from xrdpattern.core import PowderExperiment, PowderSample, CrystalStructure, Lengths, Angles, CrystalBase, Artifacts
import re

delim = ' '
with open('ruff_spgs.txt', 'r') as f:
    content = f.read()
rows = content.split('\n')
to_int_dict = {}
for r in rows:
    entries = re.split('[\t ]+', r)
    print(f'Entries are {entries}')
    try:
        i = int(entries[0])
        for s in entries[1:]:
            to_int_dict[s] = i
    except:
        pass

# ---------------------------------------------------------


@dataclass
class RRUFFLabels:
    spacegroup: str
    lattice_parameters: list
    wavelength: float


def extract_labels(fpath : str) -> RRUFFLabels:
    spg = None
    lattice_parameters = None
    wavelength = None

    with open(fpath, 'r') as file:
        lines = file.readlines()

    for line in lines:
        if "CELL PARAMETERS:" in line:
            lattice_parameters = list(map(float, line.split(':')[1].strip().split()))
        elif "SPACE GROUP:" in line:
            spg = line.split(':')[1].strip()
        elif "X-RAY WAVELENGTH:" in line:
            wavelength = float(line.split(':')[1].strip())

    print(f'Cell params, space group, wavelength = {lattice_parameters, spg, wavelength}')
    return RRUFFLabels(spacegroup=spg, lattice_parameters=lattice_parameters, wavelength=wavelength)


def extract_basename(fname):
    basename = "__".join(fname.split("__")[:2])
    return basename


not_found_spgs = set()
def to_int(rruff_spg : str) -> int:
    rruff_spg = rruff_spg.replace('-','')
    rruff_spg = rruff_spg.replace('_', '')
    # rruff_spg = rruff_spg.replace('/', '')
    print(f'Rruff spg, found in dict = {rruff_spg}, {rruff_spg in to_int_dict}')
    if not rruff_spg in to_int_dict:
        not_found_spgs.add(rruff_spg)
        print(f'Not found spgs = {not_found_spgs}')

    return to_int_dict[rruff_spg]


if __name__ == "__main__":
    rruff_dirpath = '/home/daniel/Drive/data/workspace/rruff/'
    pattern_dirpath = os.path.join(rruff_dirpath,'patterns')
    structures_dirpath = os.path.join(rruff_dirpath,'structures')
    output_dirpath = os.path.join(rruff_dirpath,'lps')

    STRUCTURE_NAME_FPATH_MAP = {}
    copper_wavelength = 1.541838

    for name in os.listdir(structures_dirpath):
        struct_basename = extract_basename(fname=name)
        print(f'Struct basename = {struct_basename}')
        STRUCTURE_NAME_FPATH_MAP[struct_basename] = os.path.join(structures_dirpath, name)


    pattern_names = os.listdir(pattern_dirpath)
    for name in pattern_names:
        pattern_fpath = os.path.join(pattern_dirpath, name)
        base_name = extract_basename(name)
        print(f'Base_name = {base_name}')

        try:
            struct_fpath = STRUCTURE_NAME_FPATH_MAP[base_name]
            print(f'\nExtracting labels from path: {struct_fpath}')
            labels = extract_labels(fpath=struct_fpath)
            spacegroup = to_int(labels.spacegroup)

            pattern = XrdPattern.load(fpath=pattern_fpath)
            for p in labels.lattice_parameters:
                if not isinstance(p, float):
                    raise ValueError(f'Expected float, got {type(p)}')
            if not isinstance(spacegroup, int):
                raise ValueError(f'Expected int, got {type(spacegroup)}')

            a,b,c,alpha, beta, gamma = labels.lattice_parameters
            lengths = Lengths(a=a, b=b, c=c)
            angles = Angles(alpha=alpha, beta=beta, gamma=gamma)

            crystal_structure = CrystalStructure(lengths=lengths, angles=angles, spacegroup=spacegroup, base=CrystalBase())
            powder = PowderSample(crystal_structure=crystal_structure)
            artifacts = Artifacts(primary_wavelength=labels.wavelength, secondary_wavelength=copper_wavelength, secondary_to_primary=0)
            pattern.label = PowderExperiment(powder=powder, artifacts=artifacts, is_simulated=False)
            pattern.save(fpath=os.path.join(output_dirpath, base_name))

        except Exception as e:
            print(f'Error tryin to parse {base_name}: {e.__class__}')

    print(f'Not found spgs are {not_found_spgs}')