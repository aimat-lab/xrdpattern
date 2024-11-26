import os
from typing import Optional

import pandas as pd

from databases.tools.csv_label import CsvLabel
from holytools.fsys import SaveManager
from xrdpattern.crystal import Lengths, Angles
from xrdpattern.pattern import PatternDB


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
        csv_fpath = os.path.join(self.raw_dirpath, dirname, 'labels.csv')
        data = pd.read_csv(csv_fpath, skiprows=1)
        data.columns = [col.strip() for col in data.columns]

        fname = [row.iloc[0].strip() for index, row in data.iterrows()]
        lengths_list = [Lengths(row['a in nm'], row['b in nm'], row['c in nm']) for index, row in data.iterrows()]
        angles_list = [Angles(row['alpha in deg'], row['beta in deg'], row['gamma in deg']) for index, row in
                       data.iterrows()]
        chemical_compositions = [row['Element Composition'] for index, row in data.iterrows()]
        spacegroups = [row['Space group number'] for index, row in data.iterrows()]

        csv_label_dict = {}
        for fname, lengths, angles, comp, spacegroup in zip(fname, lengths_list, angles_list, chemical_compositions, spacegroups):
            csv_label_dict[fname] = CsvLabel(lengths=lengths, angles=angles, chemical_composition=comp, spacegroup=spacegroup)

        pattern_dict = { SaveManager.prune_suffix(p.get_name()) : p for p in pattern_db.patterns }
        for name in pattern_dict:
            name = SaveManager.prune_suffix(fpath=name)
            csv_label =  csv_label_dict[name]
            pattern_dict[name].crystal_structure.spacegroup = csv_label.spacegroup
            pattern_dict[name].crystal_structure.lengths = csv_label.lengths
            pattern_dict[name].crystal_structure.angles = csv_label.angles
            pattern_dict[name].crystal_structure.chemical_composition = csv_label


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
        self.process_contribution(dirname='hodge_alwen_0')

if __name__ == "__main__":
    processor = DatabaseProcessor(root_dirpath='/home/daniel/aimat/opXRD/')
    processor.parse_CNRS()
    # processor.parse_USC()

