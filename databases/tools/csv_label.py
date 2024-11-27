import os
from dataclasses import dataclass

import pandas as pd

from holytools.fsys import SaveManager
from xrdpattern.crystal import Lengths, Angles, CrystalPhase
from xrdpattern.xrd import PowderExperiment


@dataclass
class CsvLabel:
    lengths : Lengths
    angles : Angles
    chemical_composition : str
    phase_fraction : float
    spacegroup : int

    def set_phase_properties(self, phase : CrystalPhase):
        phase.spacegroup = self.spacegroup
        phase.lengths = self.lengths
        phase.angles = self.angles
        phase.chemical_composition = self.chemical_composition
        phase.phase_fraction = self.phase_fraction


def get_powder_experiment(pattern_fpath : str, contrib_dirpath : str) -> PowderExperiment:
    data_dirpath = os.path.join(contrib_dirpath, 'data')
    csv_fpath = os.path.join(contrib_dirpath, 'labels.csv')

    powder_experiment = PowderExperiment.make_empty(num_phases=2)
    rel_path = os.path.relpath(pattern_fpath, start=data_dirpath)
    rel_path = standardize_path(rel_path)

    for phase_num in range(0, 2):
        csv_label_dict = get_phase_labels(csv_fpath=csv_fpath, phase_num=phase_num)
        csv_label = csv_label_dict.get(rel_path)
        if not csv_label is None:
            csv_label.set_phase_properties(phase=powder_experiment.phases[phase_num])
        else:
            print(f'Unlabeled pattern {rel_path} in contribution {os.path.basename(contrib_dirpath)}')

    return powder_experiment


def get_phase_labels(csv_fpath : str, phase_num : int) -> dict[str, CsvLabel]:
    data = pd.read_csv(csv_fpath, skiprows=1)
    increment = 0 if phase_num == 0 else 11

    rel_path = [row.iloc[0].strip() for index, row in data.iterrows()]
    chemical_compositions = [row.iloc[1 + increment] for index, row in data.iterrows()]
    phase_fractions = [row.iloc[2 + increment] for index, row in data.iterrows()]
    lengths_list = [Lengths(row.iloc[3+increment], row.iloc[4+increment], row.iloc[5+increment]) for index, row in data.iterrows()]
    angles_list = [Angles(row.iloc[6+increment], row.iloc[7+increment], row.iloc[8+increment]) for index, row in data.iterrows()]

    spacegroups = [row.iloc[9+increment] for index, row in data.iterrows()]
    spacegroups = [int(spg) if not spg != spg else spg for spg in spacegroups]

    csv_label_dict = {}
    for rel_path, lengths, angles, comp, fract, spacegroup in zip(rel_path, lengths_list, angles_list, chemical_compositions, phase_fractions, spacegroups):
        rel_path = standardize_path(fpath=rel_path)
        csv_label_dict[rel_path] = CsvLabel(lengths=lengths, angles=angles, chemical_composition=comp, spacegroup=spacegroup, phase_fraction=fract)

    return csv_label_dict

def standardize_path(fpath : str):
    fpath = SaveManager.prune_suffix(fpath)
    fpath = fpath.replace('\\','/')
    return fpath
