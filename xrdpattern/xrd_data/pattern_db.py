from __future__ import annotations

import os.path
import os
from dataclasses import dataclass

from .pattern import XrdPattern
# -------------------------------------------


@dataclass
class XrdPatternDB:
    patterns : list[XrdPattern]

    def save(self, path : str):
        is_occupied = os.path.isdir(path) or os.path.isfile(path)
        if is_occupied:
            raise ValueError(f'Path \"{path}\" is occupied by file/dir')
        os.makedirs(path, exist_ok=True)

        for pattern in self.patterns:
            fpath = os.path.join(path, pattern.get_name())
            pattern.save(fpath=fpath)
