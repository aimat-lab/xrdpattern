from dataclasses import dataclass
from .pattern import XrdPattern
from .pattern_report import ParsingReport


@dataclass
class DatabaseReport:
    data_dirpath : str
    failed_files : list[str]
    fpath_dict : dict[str, list[XrdPattern]]

    def __post_init__(self):
        self.num_err, self.num_warn = 0, 0
        self.pattern_reports : list[ParsingReport] = []
        for fpath, fpath_patterns in self.fpath_dict.items():
            self.pattern_reports += [pattern.get_parsing_report(datafile_fpath=fpath) for pattern in fpath_patterns]

        for report in self.pattern_reports:
            self.num_err += report.has_error()
        self.source_files = list(self.fpath_dict.keys()) + self.failed_files

    def print(self):
        print(self.as_str())

    def as_str(self, with_individual_reports : bool = False) -> str:
        num_failed = len(self.failed_files)
        num_attempted_files = len(self.source_files)
        num_parsed_patterns = len(self.pattern_reports)

        summary_str = f'\n----- Finished creating database from data root \"{self.data_dirpath}\" -----\n'
        if num_failed > 0:
            summary_str += f'{num_failed}/{num_attempted_files} files could not be parsed'
        else:
            summary_str += f'All pattern were successfully parsed'
        summary_str += f'\n- Processed {num_attempted_files} files to extract {num_parsed_patterns} patterns'
        summary_str += f'\n- {self.num_warn}/{num_parsed_patterns} patterns had warning(s)'
        summary_str += f'\n- {self.num_err}/{num_parsed_patterns} patterns had error(s)'

        if num_failed > 0:
            summary_str += f'\n\nFailed files:\n'
            for pattern_fpath in self.failed_files:
                summary_str += f'\n- {pattern_fpath}'

        if with_individual_reports:
            individual_reports = '\n\nIndividual file reports:\n\n'
            for pattern_health in self.pattern_reports:
                individual_reports += f'{str(pattern_health)}\n\n'
            summary_str += f'\n\n----------------------------------------{individual_reports}'

        summary_str += '\n\n----------------------------------------'

        return summary_str

