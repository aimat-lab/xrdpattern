from __future__ import annotations

import logging
import os
import traceback
from collections import Counter
from dataclasses import dataclass
from typing import Optional, Any

from matplotlib import pyplot as plt

from holytools.fsys import FsysNode
from holytools.logging import LoggerFactory
from holytools.userIO import TrackedInt

from xrdpattern.parsing import Parser, Orientation, Formats
from .pattern import XrdPattern, PatternReport

patterdb_logger = LoggerFactory.get_logger(name=__name__)

# -------------------------------------------

@dataclass
class PatternDB:
    patterns : list[XrdPattern]
    database_report : Optional[DatabaseReport] = None
    name : str = ''

    # -------------------------------------------
    # save/load

    def save(self, dirpath : str):
        if os.path.isfile(dirpath):
            raise ValueError(f'Path \"{dirpath}\" is occupied by file')
        os.makedirs(dirpath, exist_ok=True)

        def get_path(basename : str, index : Optional[int] = None):
            conditional_index = '' if index is None else f'_{index}'
            return os.path.join(dirpath, f'{basename}{conditional_index}.{Formats.aimat_xrdpattern.suffix}')

        for pattern in self.patterns:
            fpath = get_path(basename=pattern.get_name())
            current_index = 0
            while os.path.isfile(path=fpath):
                current_index += 1
                fpath = get_path(basename=pattern.get_name(), index=current_index)
            pattern.save(fpath=fpath)


    @classmethod
    def load(cls, dirpath : str, selected_suffixes : Optional[list[str]] = None,
                  default_wavelength : Optional[float] = None,
                  default_csv_orientation : Optional[Orientation] = None) -> PatternDB:

        dirpath = os.path.normpath(path=dirpath)
        if not os.path.isdir(dirpath):
            raise ValueError(f"Given path {dirpath} is not a directory")


        patterns : list[XrdPattern] = []
        parser = Parser(default_wavelength=default_wavelength, default_csv_orientation=default_csv_orientation)
        failed_fpath = []
        parsing_reports = []

        data_fpaths = cls.get_xrd_fpaths(dirpath=dirpath, selected_suffixes=selected_suffixes)
        tracker = TrackedInt(start_value=0, finish_value=len(data_fpaths))
        for fpath in data_fpaths:
            try:
                patterns += [XrdPattern(**info.to_dict()) for info in parser.extract(fpath=fpath)]
                parsing_reports += [pattern.get_parsing_report(datafile_fpath=fpath) for pattern in patterns]
                tracker.increment(to_add=1)
            except Exception as e:
                failed_fpath.append(fpath)
                patterdb_logger.log(msg=f"Could not import pattern from file {fpath}\n"
                      f"-> Error: \"{e.__class__.__name__}: {str(e)}\"\n"
                      f"-> Traceback: \n{traceback.format_exc()}", level=logging.WARNING)

        database_report = DatabaseReport(failed_files=failed_fpath,
                                         source_files=data_fpaths,
                                         pattern_reports=parsing_reports,
                                         data_dirpath=dirpath)
        return PatternDB(patterns=patterns, database_report=database_report)

    # -------------------------------------------
    # pattern database

    @staticmethod
    def get_xrd_fpaths(dirpath : str, selected_suffixes : Optional[list[str]] = None):
        if selected_suffixes is None:
            selected_suffixes = Formats.get_allowed_suffixes()
        root_node = FsysNode(path=dirpath)
        xrd_file_nodes = root_node.get_file_subnodes(select_formats=selected_suffixes)
        data_fpaths = [node.get_path() for node in xrd_file_nodes]

        return data_fpaths



    def __eq__(self, other):
        if not isinstance(other, PatternDB):
            return False
        if len(self.patterns) != len(other.patterns):
            return False
        for self_pattern, other_pattern in zip(self.patterns, other.patterns):
            if self_pattern != other_pattern:
                return False
        return True

    def plot_quantity(self, attr : str = 'crystal_structure.spacegroup', print_counts : bool = False):
        quantity_list = []
        for j,pattern in enumerate(self.patterns):
            try:
                spg = nested_getattr(pattern, attr)
                quantity_list.append(spg)
            except:
                patterdb_logger.log(msg=f'Could not extract attribute \"{attr}\" from file {pattern.get_name()}',
                                    level=logging.WARNING)
        if not quantity_list:
            raise ValueError(f'No data found for attribute {attr}')

        counts = Counter(quantity_list)
        sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)

        if print_counts:
            print(f'-> Count distribution of {attr} in Dataset:')
            for key, value in sorted_counts:
                print(f'- {key} : {value}')

        keys, values = zip(*sorted_counts)
        if len(keys) > 30:
            keys = keys[:30]
            values = values[:30]

        def attempt_round(val : Any):
            if type(val) == int:
                return val
            try:
                rounded_val = round(val,2)
            except:
                rounded_val = val
            return rounded_val

        rounded_keys = [str(attempt_round(key)) for key in keys]
        print(f'Number of data patterns with label {attr} = {len(quantity_list)}')

        plt.figure(figsize=(10, 5))
        plt.bar(rounded_keys, values)
        plt.xlabel(attr)
        plt.ylabel('Counts')
        plt.title(f'Count distribution of {attr} in Dataset {self.name}')
        plt.xticks(rotation=90)
        plt.show()


def nested_getattr(obj: object, attr_string):
    attr_names = attr_string.split('.')
    for name in attr_names:
        obj = getattr(obj, name)
    return obj


@dataclass
class DatabaseReport:
    data_dirpath : str
    failed_files : list[str]
    source_files : list[str]
    pattern_reports: list[PatternReport]

    def __post_init__(self):
        self.num_crit, self.num_err, self.num_warn = 0, 0, 0
        for report in self.pattern_reports:
            self.num_crit += report.has_critical()
            self.num_err += report.has_error()
            self.num_warn += report.has_warning()


    def get_str(self) -> str:
        num_failed = len(self.failed_files)
        num_attempted_files = len(self.source_files)
        num_parsed_patterns = len(self.pattern_reports)

        summary_str = f'\n----- Finished creating database from data root \"{self.data_dirpath}\" -----\n'
        if num_failed > 0:
            summary_str += f'{num_failed}/{num_attempted_files} files could not be parsed'
        else:
            summary_str += f'All pattern were successfully parsed'
        summary_str += f'\n- Processed {num_attempted_files} files to extract {num_parsed_patterns} patterns'
        summary_str += f'\n- {self.num_crit}/{num_parsed_patterns} patterns had had critical error(s)'
        summary_str += f'\n- {self.num_err}/{num_parsed_patterns} patterns had error(s)'
        summary_str += f'\n- {self.num_warn}/{num_parsed_patterns} patterns had warning(s)'

        if num_failed > 0:
            summary_str += f'\n\nFailed files:\n'
            for pattern_fpath in self.failed_files:
                summary_str += f'\n{pattern_fpath}'

        individual_reports = '\n\nIndividual file reports:\n\n'
        for pattern_health in self.pattern_reports:
            individual_reports += f'{str(pattern_health)}\n\n'
        summary_str += f'\n\n----------------------------------------{individual_reports}'

        return summary_str

