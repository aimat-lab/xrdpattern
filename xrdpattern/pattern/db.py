from __future__ import annotations

import os
from dataclasses import dataclass
import random
from typing import Optional

from matplotlib import pyplot as plt

from holytools.logging import LoggerFactory
from holytools.userIO import TrackedCollection
from xrdpattern.parsing import MasterParser, Formats
from xrdpattern.xrd import XrayInfo, XrdData
from .visualization import histograms, multiplot
from .pattern import XrdPattern

patterdb_logger = LoggerFactory.get_logger(name=__name__)
parser = MasterParser()

# -------------------------------------------

@dataclass
class PatternDB:
    patterns : list[XrdPattern]
    fpath_dict: dict[str, list[XrdPattern]]
    name : str = ''

    # -------------------------------------------
    # load/save

    @classmethod
    def load(cls, dirpath : str,
             strict : bool = False,
             suffixes : Optional[list[str]] = None,
             csv_orientation : Optional[str] = None) -> PatternDB:
        dirpath = os.path.normpath(path=dirpath)
        if not os.path.isdir(dirpath):
            raise ValueError(f"Given path {dirpath} is not a directory")

        data_fpaths = Formats.get_xrd_fpaths(dirpath=dirpath, selected_suffixes=suffixes)
        if len(data_fpaths) == 0:
            raise ValueError(f"No data files matching suffixes {suffixes} found in directory {dirpath}")

        patterdb_logger.info(f'Loading patterns from local dirpath {dirpath}')
        db = cls._make_empty(name=os.path.basename(dirpath))
        for fpath in TrackedCollection(data_fpaths):
            try:
                xrd_datas = parser.extract(fpath=fpath, csv_orientation=csv_orientation)
                [db._add_data(info=info, fpath=fpath, strict=strict) for info in xrd_datas]
            except Exception as e:
                patterdb_logger.warning(f'Failed to parse file {fpath}:\n- Reason: {e.__repr__()}')
                if strict:
                    raise e

        patterdb_logger.info(f'Finished loading pattern database located at {dirpath}')
        patterdb_logger.info(f'Successfully extracted {len(db.patterns)} patterns '
                             f'from {len(db.fpath_dict)}/{len(data_fpaths)} xrd files')

        return db

    @classmethod
    def _make_empty(cls, name : str = '') -> PatternDB:
        return cls(patterns=[], fpath_dict={}, name=name)

    def _add_data(self, info : XrdData, fpath : str, strict : bool):
        try:
            p = XrdPattern(**info.to_init_dict())
            if not fpath in self.fpath_dict:
                self.fpath_dict[fpath] = []
            self.fpath_dict[fpath].append(p)
            self.patterns.append(p)
        except Exception as e:
            patterdb_logger.warning(msg=f"Could not import pattern from file {fpath}:\n- Reason: \"{e}\"\n")
            if strict:
                raise e

    def save(self, dirpath : str, force_overwrite : bool = False):
        if os.path.isfile(dirpath):
            raise ValueError(f'Path \"{dirpath}\" is occupied by file')
        os.makedirs(dirpath, exist_ok=True)

        for j, patterns in enumerate(self.fpath_dict.values()):
            for k, p in enumerate(patterns):
                if len(patterns) > 1:
                    fname = f'pattern_group_{j}_{k}.{Formats.aimat_suffix()}'
                else:
                    fname = f'pattern_{j}.{Formats.aimat_suffix()}'
                fpath = os.path.join(dirpath, fname)
                p.save(fpath=fpath, force_overwrite=force_overwrite)

    # -------------------------------------------
    # operations

    def __add__(self, other : PatternDB) -> PatternDB:
        return PatternDB.merge(dbs=[self, other])

    @classmethod
    def merge(cls, dbs : list[PatternDB]):
        patterns = []
        fpath_dict = {}
        for db in dbs:
            patterns += db.patterns
            fpath_dict.update(db.fpath_dict)

        return PatternDB(patterns=patterns, fpath_dict=fpath_dict)

    def set_xray(self, xray_info : XrayInfo):
        for p in self.patterns:
            p.powder_experiment.xray_info = xray_info

    # -------------------------------------------
    # view

    def __eq__(self, other : PatternDB):
        if not isinstance(other, PatternDB):
            return False
        if len(self.patterns) != len(other.patterns):
            return False
        for self_pattern, other_pattern in zip(self.patterns, other.patterns):
            if self_pattern != other_pattern:
                return False
        return True

    def show_all(self, single_plot : bool = False, limit_patterns : int = 100, title : Optional[str] = None):
        patterns = self.patterns if len(self.patterns) <= limit_patterns else random.sample(self.patterns, limit_patterns)
        if single_plot:
            data = [p.get_pattern_data() for p in patterns]
            fig, ax = plt.subplots(dpi=600)
            for x, y in data:
                ax.plot(x, y, linewidth=0.25, alpha=0.75)

            ax.set_xlabel(r'$2\theta$ [$^\circ$]')
            ax.set_ylabel('Standardized relative intensity (a.u.)')
            if title:
                ax.set_title(title)
            else:
                ax.set_title(f'XRD Patterns from {self.name}')
            plt.show()

        else:
            batch_size = 32
            j = 0
            while j < len(patterns):
                pattern_batch = patterns[j:j + batch_size]
                for k, p in enumerate(pattern_batch):
                    p.metadata.filename = p.get_name() or f'pattern_{j + k}'
                multiplot(patterns=pattern_batch, start_idx=j)
                j += batch_size

                user_input = input(f'Press enter to continue or q to quit')
                if user_input.lower() == 'q':
                    break

    def show_histograms(self, save_fpath : Optional[str] = None, attach_colorbar : bool = True):
        histograms(patterns=self.patterns, attach_colorbar=attach_colorbar, save_fpath=save_fpath)


