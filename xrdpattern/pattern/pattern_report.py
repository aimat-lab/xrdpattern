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

