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

    # -------------------------------------------
    # save/load

    def save(self, path : str):
        is_occupied = os.path.isdir(path) or os.path.isfile(path)
        if is_occupied:
            raise ValueError(f'Path \"{path}\" is occupied by file/dir')
        os.makedirs(path, exist_ok=True)
        for pattern in self.patterns:
            fpath = os.path.join(path, pattern.get_name())
            pattern.save(fpath=fpath)

    @classmethod
    def load(cls, datafolder_path : str, parser_options : ParserOptions) -> PatternDB:
        parser = Parser(parser_options=parser_options)
        if not os.path.isdir(datafolder_path):
            raise ValueError(f"Given path {datafolder_path} is not a directory")

        patterns = []
        data_fpaths = PatternDB.get_datafile_fpaths(datafolder_path=datafolder_path,
                                                    select_formats=parser_options.select_suffixes)

        for fpath in data_fpaths:
            try:
                pattern_info_list = parser.get_pattern_info_list(fpath=fpath)
                new_patterns = [from_info(pattern_info=pattern_info, fpath=fpath) for pattern_info in pattern_info_list]
                patterns += new_patterns
            except Exception as e:
                print(f"Could not import pattern from file {fpath} \n"
                      f"-> Error: \"{e.__class__.__name__}: {str(e)}\"")
        return PatternDB(patterns=patterns)

    # -------------------------------------------
    # pattern database

    @classmethod
    def get_datafile_fpaths(cls, datafolder_path : str, select_formats : Optional[list[str]] = None) -> list[str]:
        root_node = FsysNode(path=datafolder_path)
        xrd_files_nodes = root_node.get_file_subnodes(select_formats=select_formats)
        return [node.get_path() for node in xrd_files_nodes]


    def get_parsing_report(self, num_files : int, num_failed : int) -> DatabaseReport:
        reports = [pattern.get_parsing_report() for pattern in self.patterns]
        database_health = DatabaseReport(num_data_files=num_files, num_failed=num_failed, pattern_reports=reports)
        pattern_healths = [pattern.get_parsing_report() for pattern in self.patterns]
        for report in pattern_healths:
            database_health.num_crit += report.has_critical()
            database_health.num_err += report.has_error()
            database_health.num_warn += report.has_warning()
        return database_health


@dataclass
class DatabaseReport:
    num_data_files : int
    num_failed : int
    pattern_reports: list[PatternReport]
    num_crit: int = 0
    num_err : int = 0
    num_warn : int = 0

    def get_str(self) -> str:
        summary_str = f'\n----- Finished creating database -----'
        if self.num_failed > 0:
            summary_str += f'\n{self.num_failed}/{self.num_data_files} files could not be parsed'
        else:
            summary_str += f'\nAll patterns were successfully parsed'
        summary_str += f'\n{self.num_crit}/{self.num_data_files} patterns had critical error(s)'
        summary_str += f'\n{self.num_err}/{self.num_data_files}  patterns had error(s)'
        summary_str += f'\n{self.num_warn}/{self.num_data_files}  patterns had warning(s)'

        individual_reports = '\n\nIndividual file reports:\n\n'
        for pattern_health in self.pattern_reports:
            individual_reports += f'{str(pattern_health)}\n\n'
        summary_str += f'\n\n----------------------------------------{individual_reports}'

        return summary_str



def from_info(pattern_info : PatternInfo, fpath : str)-> XrdPattern:
    return XrdPattern(intensity_map=pattern_info.intensity_map, metadata=pattern_info.metadata, datafile_path=fpath)
