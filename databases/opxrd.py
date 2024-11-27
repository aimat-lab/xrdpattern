import os
from typing import Optional

from databases.tools.csv_label import standardize_path, get_phase_labels, get_powder_experiment
from holytools.fsys import SaveManager
from holytools.logging.tools import log_execution
from xrdpattern.crystal import CrystalPhase
from xrdpattern.pattern import PatternDB
from xrdpattern.xrd import PowderExperiment

# -------------------------------------------

class DatabaseProcessor:
    def __init__(self, root_dirpath : str):
        self.root_dirpath : str = root_dirpath
        self.raw_dirpath : str = os.path.join(root_dirpath, 'raw')
        self.processed_dirpath : str = os.path.join(root_dirpath, 'processed')

    def process_contribution(self, dirname: str, selected_suffixes : Optional[list[str]] = None, use_cif_labels : bool = False):
        print(f'Started processing contributino {dirname}')
        data_dirpath = os.path.join(self.raw_dirpath, dirname, 'data')
        pattern_db = PatternDB.load(dirpath=data_dirpath, selected_suffixes=selected_suffixes)

        self.attach_metadata(pattern_db, dirname=dirname)
        labeling_routine = self.attach_cif_labels if use_cif_labels else self.attach_labels
        labeling_routine(pattern_db=pattern_db, dirname=dirname)
        self.save(pattern_db, dirname=dirname)

    # ---------------------------------------
    # Parsing steps

    @log_execution
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


    @log_execution
    def attach_cif_labels(self, pattern_db : PatternDB):
        for fpath, patterns in pattern_db.fpath_dict.items():
            dirpath = os.path.basename(fpath)
            cif_fnames = [fname for fname in os.listdir(dirpath) if SaveManager.get_suffix(fname) == 'cif']

            powder_experiment = PowderExperiment.make_empty()
            for fname in cif_fnames:
                cif_content = read_file(fpath=os.path.join(dirpath, fname))
                powder_experiment.material_phases.append(CrystalPhase.from_cif(cif_content))

            for p in patterns:
                p.powder_experiment = powder_experiment


    @log_execution
    def attach_labels(self, pattern_db : PatternDB, contrib_dirpath : str):
        csv_fpath = os.path.join(contrib_dirpath, 'labels.csv')
        if not os.path.isfile(csv_fpath):
            print(f'No labels available for contribution {os.path.basename(contrib_dirpath)}')
            return

        for p in pattern_db.patterns:
            if p.powder_experiment.is_nonempty():
                raise ValueError(f"Pattern {p.get_name()} is already labeled")

        for pattern_fpath, file_patterns in pattern_db.fpath_dict.items():
            powder_experiment = get_powder_experiment(pattern_fpath=pattern_fpath, contrib_dirpath=contrib_dirpath)

            for p in file_patterns:
                p.powder_experiment = powder_experiment


    @log_execution
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
        self.process_contribution(dirname='hodge_alwen_1')

    def parse_EMPA(self):
        self.process_contribution(dirname='siol_wieczorek_0')
        self.process_contribution(dirname='siol_zhuk_0')

    def parse_IKFT(self):
        self.process_contribution(dirname='wolf_wolf_0')

    def parse_HKUST(self):
        self.process_contribution(dirname='zhang_cao_0', use_cif_labels=True, selected_suffixes=['xy'])




def read_file(fpath: str) -> str:
    with open(fpath, 'r') as file:
        cif_content = file.read()
    return cif_content

if __name__ == "__main__":
    processor = DatabaseProcessor(root_dirpath='/home/daniel/aimat/opXRD/')
    # processor.parse_EMPA()
    # processor.parse_IKFT()
    processor.parse_HKUST()


