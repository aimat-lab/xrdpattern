import os
from dataclasses import dataclass
from typing import Optional

from xrdpattern.pattern import PatternDB
# -------------------------------------------

@dataclass
class ContributorInfo:
    institution : str
    name_advisor : str

class DatabaseProcessor:
    def __init__(self, root_dirpath : str):
        self.root_dirpath : str = root_dirpath
        self.raw_dirpath : str = os.path.join(root_dirpath, 'raw')
        self.processed_dirpath : str = os.path.join(root_dirpath, 'processed')

    def process_contribution(self, dirname: str, selected_suffixes : Optional[list[str]] = None):
        contribution_dirpath = os.path.join(self.raw_dirpath, dirname)
        info = self.get_contributor_info(contribution_dirpath=contribution_dirpath)

        data_dirpath = os.path.join(contribution_dirpath, 'data')
        pattern_db = PatternDB.load(dirpath=data_dirpath, selected_suffixes=selected_suffixes)
        for p in pattern_db.patterns:
            p.metadata.contributor_name = info.name_advisor
            p.metadata.institution = info.institution

        out_dirpath = os.path.join(self.processed_dirpath, dirname)
        if not os.path.isdir(out_dirpath):
            os.makedirs(out_dirpath)
        pattern_db.save(dirpath=out_dirpath)

    @staticmethod
    def get_contributor_info(contribution_dirpath : str) -> ContributorInfo:
        with open(f"{contribution_dirpath}/form.txt", "r") as file:
            lines = file.readlines()
        form_data = {}
        for line in lines:
            if '=' in line:
                key, value = line.strip().split('=', 1)
                form_data[key] = value

        personal_info = ContributorInfo(
            institution=form_data["contributing_institution"],
            name_advisor=form_data["name_of_advisor"]
        )
        return personal_info

    # ---------------------------------------
    # Parsing individual contributions

    def parse_INT(self):
        self.process_contribution(dirname='breitung_schweidler_0', selected_suffixes=['raw'])
        self.process_contribution(dirname='breitung_schweidler_1', selected_suffixes=['raw'])

    def parse_CNRS(self):
        self.process_contribution(dirname='coudert_hardiagon_0', selected_suffixes=['json'])


if __name__ == "__main__":
    processor = DatabaseProcessor(root_dirpath='/home/daniel/aimat/opXRD/')
    processor.parse_INT()

