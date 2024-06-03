import os

from dataclasses import dataclass
from xrdpattern.pattern import XrdPattern
from xrdpattern.core import Labels, Powder, CrystalStructure, Lengths, Angles, CrystalBase, Artifacts

rruff_dirpath = ''

@dataclass
class RRUFFLabels:
    space_group: str
    lattice_parameters: list
    wavelength: float


def extract_labels(fpath : str) -> RRUFFLabels:
    space_group = None
    lattice_parameters = None
    wavelength = None

    with open(fpath, 'r') as file:
        lines = file.readlines()

    for line in lines:
        if "CELL PARAMETERS:" in line:
            lattice_parameters = list(map(float, line.split(':')[1].strip().split()))
        elif "SPACE GROUP:" in line:
            space_group = line.split(':')[1].strip()
        elif "X-RAY WAVELENGTH:" in line:
            wavelength = float(line.split(':')[1].strip())

    print(f'Cell params, space group, wavelength = {lattice_parameters, space_group, wavelength}')
    return RRUFFLabels(space_group=space_group, lattice_parameters=lattice_parameters, wavelength=wavelength)


def extract_basename(fname):
    basename = "__".join(fname.split("__")[:2])
    return basename

def to_int(rruff_spg : str) -> int:
    spg_number = None
    if rruff_spg == "Fm3m":
        rruff_spg = "Fm-3m"
    elif rruff_spg == "Pncm":
        spg_number = 53
    elif rruff_spg == "C-1":
        spg_number = 1
    elif (
            rruff_spg == "P21/n"
            or rruff_spg == "P21/a"
            or rruff_spg == "P21/b"
    ):
        spg_number = 14
    elif (
            rruff_spg == "Pbnm"
            or rruff_spg == "Pcmn"
            or rruff_spg == "Pnam"
    ):
        spg_number = 62
    elif rruff_spg == "Amma":
        spg_number = 63
    elif rruff_spg == "Fd2d":
        spg_number = 43
    elif rruff_spg == "Fd3m":
        rruff_spg = "Fd-3m"
    elif (
            rruff_spg == "A2/a"
            or rruff_spg == "I2/a"
            or rruff_spg == "I2/c"
    ):
        spg_number = 15
    elif rruff_spg == "P4/n":
        spg_number = 85
    elif rruff_spg == "I41/acd":
        spg_number = 142
    elif rruff_spg == "I41/amd":
        spg_number = 141
    elif rruff_spg == "Pmcn":
        spg_number = 62
    elif rruff_spg == "I41/a":
        spg_number = 88
    elif rruff_spg == "Pbn21" or rruff_spg == "P21nb":
        spg_number = 33
    elif rruff_spg == "P2cm":
        spg_number = 28
    elif rruff_spg == "P4/nnc":
        spg_number = 126
    elif rruff_spg == "Pn21m":
        spg_number = 31
    elif rruff_spg == "B2/b":
        spg_number = 15
    elif rruff_spg == "Cmca":
        spg_number = 64
    elif rruff_spg == "I2/m" or rruff_spg == "A2/m":
        spg_number = 12
    elif rruff_spg == "Pcan":
        spg_number = 60
    elif rruff_spg == "Ia3d":
        rruff_spg = "Ia-3d"
    elif rruff_spg == "P4/nmm":
        spg_number = 129
    elif rruff_spg == "Pa3":
        rruff_spg = "Pa-3"
    elif rruff_spg == "P4/ncc":
        spg_number = 130
    elif rruff_spg == "Imam":
        spg_number = 74
    elif rruff_spg == "Pmmn":
        spg_number = 59
    elif rruff_spg == "Pncn" or rruff_spg == "Pbnn":
        spg_number = 52
    elif rruff_spg == "Bba2":
        spg_number = 41
    elif rruff_spg == "C1":
        spg_number = 1
    elif rruff_spg == "Pn3":
        rruff_spg = "Pn-3"
    elif rruff_spg == "Fddd":
        spg_number = 70
    elif rruff_spg == "Pcab":
        spg_number = 61
    elif rruff_spg == "P2/a":
        spg_number = 13
    elif rruff_spg == "Pmnb":
        spg_number = 62
    elif rruff_spg == "I-1":
        spg_number = 2
    elif rruff_spg == "Pmnb":
        spg_number = 154
    elif rruff_spg == "B2mb":
        spg_number = 40
    elif rruff_spg == "Im3":
        rruff_spg = "Im-3"
    elif rruff_spg == "Pn21a":
        spg_number = 33
    elif rruff_spg == "Pm2m":
        spg_number = 25
    elif rruff_spg == "Fd3":
        rruff_spg = "Fd-3"
    elif rruff_spg == "Im3m":
        rruff_spg = "Im-3m"
    elif rruff_spg == "Cmma":
        spg_number = 67
    elif rruff_spg == "Pn3m":
        rruff_spg = "Pn-3m"
    elif rruff_spg == "F2/m":
        spg_number = 12
    elif rruff_spg == "Pnm21":
        spg_number = 31

    if spg_number is None:
        raise ValueError(f'Could not convert {rruff_spg} to space group number')

    return spg_number

if __name__ == "__main__":
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
            spacegroup = to_int(labels.space_group)

            pattern = XrdPattern.load(fpath=pattern_fpath)
            for p in labels.lattice_parameters:
                if not isinstance(p, float):
                    raise ValueError(f'Expected float, got {type(p)}')
            if not isinstance(spacegroup, int):
                raise ValueError(f'Expected int, got {type(spacegroup)}')

            a,b,c,alpha, beta, gamma = labels.lattice_parameters
            lengths = Lengths(a=a, b=b, c=c)
            angles = Angles(alpha=alpha, beta=beta, gamma=gamma)

            crystal_structure = CrystalStructure(lengths=lengths, angles=angles, space_group=spacegroup, base=CrystalBase())
            powder = Powder(crystal_structure=crystal_structure)
            artifacts = Artifacts(primary_wavelength=labels.wavelength, secondary_wavelength=copper_wavelength, secondary_to_primary=0)
            pattern.label = Labels(powder=powder, artifacts=artifacts, is_simulated=False)
            pattern.save(fpath=os.path.join(output_dirpath, base_name))

        except Exception as e:
            print(f'Error tryin to parse {base_name}: {e.__class__}')

