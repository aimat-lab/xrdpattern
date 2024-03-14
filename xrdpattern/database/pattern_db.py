from __future__ import annotations

import os.path
import os
from dataclasses import dataclass
from xrdpattern.pattern import XrdPattern
# -------------------------------------------


@dataclass
class XrdPatternDB:
    patterns : list[XrdPattern]
    num_data_files : int

    def save(self, path : str):
        is_occupied = os.path.isdir(path) or os.path.isfile(path)
        if is_occupied:
            raise ValueError(f'Path \"{path}\" is occupied by file/dir')
        os.makedirs(path, exist_ok=True)

        for pattern in self.patterns:
            fpath = os.path.join(path, pattern.get_name())
            pattern.save(fpath=fpath)


    def create_report(self, fpath : str) -> str:
        num_unsuccessful = self.total_count-len(self.patterns)
        summary_str =(f'\n----- Finished creating database -----'
                      f'\n{num_unsuccessful}/{self.total_count} patterns could not be parsed')


        num_crit, num_err, num_warn = 0,0,0
        reports = [pattern.processing_report for pattern in self.patterns]
        for report in reports:
            num_crit += report.has_critical_error()
            num_err += report.has_error()
            num_warn += report.has_warning()

        summary_str += f'\n{num_crit}/{self.total_count} patterns had critical error(s)'
        summary_str += f'\n{num_err}/{self.total_count}  patterns had error(s)'
        summary_str += f'\n{num_warn}/{self.total_count}  patterns had warning(s)'
        log(f'{summary_str}\n\n'
            f'----------------------------------------\n')

        log(f'Individual file reports\n\n')
        for pattern in self.patterns:
            log(msg=str(pattern.processing_report))


