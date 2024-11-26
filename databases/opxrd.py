import os
from typing import Optional

import pandas as pd

from databases.tools.csv_label import CsvLabel
from holytools.fsys import SaveManager
from xrdpattern.crystal import Lengths, Angles
from xrdpattern.pattern import PatternDB
from xrdpattern.xrd import PowderExperiment


# -------------------------------------------


class DatabaseProcessor:
    def __init__(self, root_dirpath : str):
        self.root_dirpath : str = root_dirpath
        self.raw_dirpath : str = os.path.join(root_dirpath, 'raw')
        self.processed_dirpath : str = os.path.join(root_dirpath, 'processed')

    def process_contribution(self, dirname: str, selected_suffixes : Optional[list[str]] = None):
        data_dirpath = os.path.join(self.raw_dirpath, dirname, 'data')
        pattern_db = PatternDB.load(dirpath=data_dirpath, selected_suffixes=selected_suffixes, store_filenames=True)

        self.attach_metadata(pattern_db, dirname=dirname)
        self.attach_labels(pattern_db, dirname=dirname)
        self.save(pattern_db, dirname=dirname)

    # ---------------------------------------
    # Parsing steps

    def attach_metadata(self, pattern_db : PatternDB, dirname : str):
        form_dirpath = os.path.join(self.raw_dirpath, dirname, 'form.txt')
        with open(form_dirpath, "r") as file:
            lines = file.readlines()
        form_data = {}
        for line in lines:
            if '=' in line:
                key, value = line.strip().split('=', 1)
                form_data[key] = value

        for p in pattern_db.patterns:
            p.metadata.contributor_name = form_data["name_of_advisor"]
            p.metadata.institution = form_data["contributing_institution"]


    def attach_labels(self, pattern_db : PatternDB, dirname : str):
        for p in pattern_db.patterns:
            if p.powder_experiment.is_nonempty():
                raise ValueError(f"Pattern {p.get_name()} is already labeled")

        pattern_dict = {SaveManager.prune_suffix(p.get_name()): p for p in pattern_db.patterns}
        csv_fpath = os.path.join(self.raw_dirpath, dirname, 'labels.csv')

        for name in pattern_dict:
            powder_experiment = PowderExperiment.make_empty(num_phases=2)
            name = SaveManager.prune_suffix(fpath=name)

            for phase_num in range(1, 3):
                csv_label_dict = self.get_phase_labels(csv_fpath=csv_fpath, phase_num=phase_num)
                csv_label = csv_label_dict[name]

                phase = powder_experiment.material_phases[phase_num]
                phase.spacegroup = csv_label.spacegroup
                phase.lengths = csv_label.lengths
                phase.angles = csv_label.angles
                phase.chemical_composition = csv_label.chemical_composition

            pattern_dict[name].powder_experiment = powder_experiment

    @staticmethod
    def get_phase_labels(csv_fpath : str, phase_num : int) -> dict[str, CsvLabel]:
        data = pd.read_csv(csv_fpath, skiprows=1)
        increment = 0 if phase_num == 0 else 10

        fname = [row.iloc[0].strip() for index, row in data.iterrows()]
        lengths_list = [Lengths(row.iloc[4+increment], row.iloc[5+increment], row.iloc[6+increment]) for index, row in data.iterrows()]
        angles_list = [Angles(row.iloc[7+increment], row.iloc[8+increment], row.iloc[9+increment]) for index, row in data.iterrows()]

        chemical_compositions = [row.iloc[2+increment] for index, row in data.iterrows()]
        spacegroups = [row.iloc[10+increment] for index, row in data.iterrows()]
        spacegroups = [int(spg) if not spg != spg else spg for spg in spacegroups]

        csv_label_dict = {}
        for fname, lengths, angles, comp, spacegroup in zip(fname, lengths_list, angles_list, chemical_compositions, spacegroups):
            csv_label_dict[fname] = CsvLabel(lengths=lengths, angles=angles, chemical_composition=comp, spacegroup=spacegroup)

        print(csv_label_dict)
        return csv_label_dict


    def save(self, pattern_db : PatternDB, dirname : str):
        out_dirpath = os.path.join(self.processed_dirpath, dirname)
        if not os.path.isdir(out_dirpath):
            os.makedirs(out_dirpath)
        pattern_db.save(dirpath=out_dirpath)

    # ---------------------------------------
    # Parsing individual contributions

    def parse_INT(self):
        self.process_contribution(dirname='breitung_schweidler_0', selected_suffixes=['raw'])
        self.process_contribution(dirname='breitung_schweidler_1', selected_suffixes=['raw'])

    def parse_CNRS(self):
        self.process_contribution(dirname='coudert_hardiagon_0', selected_suffixes=['json'])

    def parse_USC(self):
        self.process_contribution(dirname='hodge_alwen_1')

if __name__ == "__main__":
    processor = DatabaseProcessor(root_dirpath='/home/daniel/aimat/opXRD/')
    # processor.parse_CNRS()
    processor.parse_USC()

