from __future__ import annotations

import os
import random
from dataclasses import dataclass
from typing import Optional

import matplotlib.gridspec as gridspec
from matplotlib import pyplot as plt

from holytools.logging import LoggerFactory
from holytools.userIO import TrackedCollection
from xrdpattern.parsing import MasterParser, Formats
from xrdpattern.xrd import XrayInfo, XrdData
from .pattern import XrdPattern
from .visualization import multiplot, define_angle_start_stop_ax, define_recorded_angles_ax, define_spg_ax

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
             limit_patterns: Optional[int] = None,
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
                err_msg = f'Failed to parse file {fpath}:\n- Reason: {e.__repr__()}'
                if strict:
                    raise ValueError(err_msg)
                else:
                    patterdb_logger.warning(err_msg)

            if not limit_patterns is None:
                if len(db.patterns) >= limit_patterns:
                    break

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

    def save(self, dirpath : str, skip_if_occupied : bool = True):
        is_occupied = os.path.isfile(dirpath) or os.path.isdir(dirpath)
        if is_occupied and skip_if_occupied:
            patterdb_logger.warning(f'Path \"{dirpath}\" already exists. Skipping save operation')
            return

        os.makedirs(dirpath, exist_ok=True)
        for j, patterns in enumerate(self.fpath_dict.values()):
            for k, p in enumerate(patterns):
                if len(patterns) > 1:
                    fname = f'pattern_group_{j}_{k}.{Formats.aimat_suffix()}'
                else:
                    fname = f'pattern_{j}.{Formats.aimat_suffix()}'
                fpath = os.path.join(dirpath, fname)
                p.save(fpath=fpath, force_overwrite=True)

    # -------------------------------------------
    # operations

    @classmethod
    def merge(cls, dbs : list[PatternDB]):
        patterns = []
        fpath_dict = {}
        for db in dbs:
            patterns += db.patterns
            fpath_dict.update(db.fpath_dict)

        return PatternDB(patterns=patterns, fpath_dict=fpath_dict)

    def __add__(self, other : PatternDB) -> PatternDB:
        return PatternDB.merge(dbs=[self, other])

    def set_xray(self, xray_info : XrayInfo):
        for p in self.patterns:
            p.powder_experiment.xray_info = xray_info

    def __eq__(self, other : PatternDB):
        if not isinstance(other, PatternDB):
            return False
        if len(self.patterns) != len(other.patterns):
            return False
        for self_pattern, other_pattern in zip(self.patterns, other.patterns):
            if self_pattern != other_pattern:
                return False
        return True

    # -------------------------------------------
    # view

    def plot_combined(self, max_patterns : int = 10 ** 4, title : Optional[str] = None, save_fpath : Optional[str] = None):
        patterns = self.patterns if len(self.patterns) <= max_patterns else random.sample(self.patterns, max_patterns)
        data = [p.get_pattern_data() for p in patterns]
        fig, ax = plt.subplots(dpi=600)
        for x, y in data:
            ax.plot(x, y, linewidth=0.25, alpha=0.75, linestyle='--')

        ax.set_xlabel(r'$2\theta$ [$^\circ$]')
        ax.set_ylabel('Standardized relative intensity (a.u.)')
        if title:
            ax.set_title(title)
        else:
            ax.set_title(f'XRD Patterns from {self.name}')

        if save_fpath:
            plt.savefig(save_fpath)
        plt.show()

    def show_gallery(self):
        patterns = random.sample(self.patterns, len(self.patterns))
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
        fig = plt.figure(figsize=(12, 8))

        figure = gridspec.GridSpec(nrows=2, ncols=1, figure=fig, hspace=0.35)
        figure.update(top=0.96, bottom=0.075)
        upper_half = figure[0].subgridspec(1, 3)
        ax2 = fig.add_subplot(upper_half[:, :])
        define_spg_ax(patterns=self.patterns, ax=ax2)

        lower_half = figure[1].subgridspec(1, 2)
        ax3 = fig.add_subplot(lower_half[:, 0])
        define_recorded_angles_ax(patterns=self.patterns, ax=ax3)

        if attach_colorbar:
            lower_half_right = lower_half[1].subgridspec(nrows=3, ncols=3, width_ratios=[3, 3, 4] , hspace=0, wspace=0)
            ax4 = fig.add_subplot(lower_half_right[1:, :2])  # scaatter
            ax5 = fig.add_subplot(lower_half_right[:1, :2], sharex=ax4)  # Above
            ax6 = fig.add_subplot(lower_half_right[1:, 2:], sharey=ax4)  # Right
            ax7 = fig.add_subplot(lower_half_right[:1, 2:])
            ax7.axis('off')
        else:
            lower_half_right = lower_half[1].subgridspec(nrows=3, ncols=4, width_ratios=[2.75, 3, 3, 3], hspace=0, wspace=0)
            ax4 = fig.add_subplot(lower_half_right[1:, 1:3])  # scatter
            ax5 = fig.add_subplot(lower_half_right[:1, 1:3], sharex=ax4)  # Above
            ax6 = fig.add_subplot(lower_half_right[1:, 3:4], sharey=ax4)  # Right
            ax7 = fig.add_subplot(lower_half_right[:4, :1])

        define_angle_start_stop_ax(patterns=self.patterns, density_ax=ax4, top_marginal=ax5, right_marginal=ax6, cmap_ax=ax7, attach_colorbar=attach_colorbar)

        if save_fpath:
            plt.savefig(save_fpath)
        plt.show()



