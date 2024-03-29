from __future__ import annotations
import os
from typing import Optional
from dataclasses import dataclass

from xrdpattern.core import PatternInfo
from hollarek.fsys import FsysNode
from xrdpattern.parsing import ParserOptions, Parser
from xrdpattern.pattern import XrdPattern, PatternReport
# -------------------------------------------

@dataclass
class PatternDB:
    patterns : list[XrdPattern]
    database_report : Optional[DatabaseReport] = None

    # -------------------------------------------
    # save/load

    def save(self, path : str):
        is_occupied = os.path.isdir(path) or os.path.isfile(path)
        if is_occupied:
            raise ValueError(f'Path \"{path}\" is occupied by file/dir')
        os.makedirs(path, exist_ok=True)
        for pattern in self.patterns:
            # fpath = os.path.join(path, f'{pattern.get_name()}.json')
            fpath = os.path.join(path, pattern.get_name())
            # print(f'fpath is currently {fpath}')
            pattern.save(fpath=fpath)

    @classmethod
    def load(cls, datafolder_path : str, parser_options : ParserOptions = ParserOptions()) -> PatternDB:
        datafolder_path = os.path.normpath(path=datafolder_path)

        parser = Parser(parser_options=parser_options)
        if not os.path.isdir(datafolder_path):
            raise ValueError(f"Given path {datafolder_path} is not a directory")

        patterns = []
        data_fpaths = PatternDB.get_datafile_fpaths(datafolder_path=datafolder_path,
                                                    select_formats=parser_options.select_suffixes)

        failed_fpath = []
        for fpath in data_fpaths:
            try:
                pattern_info_list = parser.get_pattern_info_list(fpath=fpath)
                new_patterns = [from_info(pattern_info=pattern_info, fpath=fpath) for pattern_info in pattern_info_list]
                patterns += new_patterns
            except Exception as e:
                failed_fpath.append(fpath)
                print(f"Could not import pattern from file {fpath} \n"
                      f"-> Error: \"{e.__class__.__name__}: {str(e)}\"")

        reports = [pattern.get_parsing_report() for pattern in patterns]
        database_report = DatabaseReport(failed_files=failed_fpath, source_files=data_fpaths, pattern_reports=reports)
        return PatternDB(patterns=patterns, database_report=database_report)

    # -------------------------------------------
    # pattern database

    @classmethod
    def get_datafile_fpaths(cls, datafolder_path : str, select_formats : Optional[list[str]] = None) -> list[str]:
        root_node = FsysNode(path=datafolder_path)
        xrd_files_nodes = root_node.get_file_subnodes(select_formats=select_formats)
        return [node.get_path() for node in xrd_files_nodes]

    def __eq__(self, other):
        if not isinstance(other, PatternDB):
            return False
        if len(self.patterns) != len(other.patterns):
            return False
        for self_pattern, other_pattern in zip(self.patterns, other.patterns):
            if self_pattern != other_pattern:
                return False
        return True


@dataclass
class DatabaseReport:
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
        num_attempted = len(self.source_files)

        summary_str = f'\n----- Finished creating database -----'
        if num_failed > 0:
            summary_str += f'\n{num_failed}/{num_attempted} files could not be parsed'
        else:
            summary_str += f'\nAll patterns were successfully parsed'
        summary_str += f'\n{self.num_crit}/{num_attempted} patterns had critical error(s)'
        summary_str += f'\n{self.num_err}/{num_attempted}  patterns had error(s)'
        summary_str += f'\n{self.num_warn}/{num_attempted}  patterns had warning(s)'

        if num_failed > 0:
            summary_str += f'\n\nFailed files:\n'
            for pattern_fpath in self.failed_files:
                summary_str += f'\n{pattern_fpath}'

        individual_reports = '\n\nIndividual file reports:\n\n'
        for pattern_health in self.pattern_reports:
            individual_reports += f'{str(pattern_health)}\n\n'
        summary_str += f'\n\n----------------------------------------{individual_reports}'

        return summary_str



def from_info(pattern_info : PatternInfo, fpath : str)-> XrdPattern:
    return XrdPattern(xrd_data=pattern_info.xrd_data, metadata=pattern_info.metadata, datafile_path=fpath)
