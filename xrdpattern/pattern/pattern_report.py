from dataclasses import dataclass, field
from typing import Optional
# -------------------------------------------

@dataclass
class ParsingReport:
    datafile_fpath: Optional[str]
    errors: list[str] = field(default_factory=list)

    def has_error(self):
        return len(self.errors) != 0

    def add_error(self, msg : str):
        self.errors.append(f'\n{msg}')

    def as_str(self):
        report_str = f'--- Successfully processed file ---'
        data_file_info = self.datafile_fpath if self.datafile_fpath else 'Unavailable'
        report_str += f'\nData file path: {data_file_info}'
        report_str += f'\nNum errors: {len(self.errors)}'

        if len(self.errors) != 0:
            report_str += f'\nFound errors:'
            for error_msg in self.errors:
                report_str += error_msg

        report_str += '\n'
        return report_str

    def __str__(self):
        return self.as_str()


