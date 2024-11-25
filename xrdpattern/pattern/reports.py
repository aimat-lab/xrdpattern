from dataclasses import dataclass, field
from typing import Optional
# -------------------------------------------

@dataclass
class PatternReport:
    datafile_fpath: Optional[str]
    critical_errors: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def has_critical(self):
        return len(self.critical_errors) != 0

    def has_error(self):
        return len(self.errors) != 0

    def has_warning(self):
        return len(self.warnings) != 0

    def add_critical(self, msg : str):
        self.critical_errors.append(f'\n{msg}')

    def add_error(self, msg : str):
        self.errors.append(f'\n{msg}')

    def add_warning(self, msg : str):
        self.warnings.append(f'\n{msg}')

    def get_report_str(self):
        report_str = f'--- Successfully processed file ---'
        data_file_info = self.datafile_fpath if self.datafile_fpath else 'Unavailable'
        report_str += f'\nData file path: {data_file_info}'
        report_str += f'\nNum critical errors: {len(self.critical_errors)}'
        report_str += f'\nNum errors: {len(self.errors)}'
        report_str += f'\nNum warnings: {len(self.warnings)}\n'

        if len(self.critical_errors) != 0:
            report_str += f'\nFound critical errors:'
            for crit_error_msg in self.critical_errors:
                report_str += crit_error_msg

        if len(self.errors) != 0:
            report_str += f'\nFound errors:'
            for error_msg in self.errors:
                report_str += error_msg

        if len(self.warnings) != 0:
            report_str += f'\nFound warnings:'
            for warning_msg in self.warnings:
                report_str += warning_msg
        report_str += '\n'
        return report_str

    def __str__(self):
        return self.get_report_str()



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

