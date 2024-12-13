from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

import matplotlib.gridspec as gridspec
import seaborn as sns
from matplotlib import pyplot as plt
from matplotlib.axes import Axes

from databases.tools.spg_converter import SpacegroupConverter
from holytools.logging import LoggerFactory
from holytools.userIO import TrackedCollection
from xrdpattern.parsing import MasterParser, Formats, Orientation
from xrdpattern.xrd import XRayInfo, XrdPatternData
from .analysis_tools import multiplot, get_valid_values, get_counts
from .db_report import DatabaseReport
from .pattern import XrdPattern

patterdb_logger = LoggerFactory.get_logger(name=__name__)
parser = MasterParser()

# -------------------------------------------

@dataclass
class PatternDB:
    patterns : list[XrdPattern]
    failed_files : set[str]
    fpath_dict: dict[str, list[XrdPattern]]
    name : str = ''

    # -------------------------------------------
    # save/load

    def save(self, dirpath : str, label_groups : bool = False, force_overwrite : bool = False):
        if os.path.isfile(dirpath):
            raise ValueError(f'Path \"{dirpath}\" is occupied by file')
        os.makedirs(dirpath, exist_ok=True)

        if label_groups:
            for j, patterns in enumerate(self.fpath_dict.values()):
                for k, p in enumerate(patterns):
                    fpath = os.path.join(dirpath, f'pattern_group_{j}_{k}.{Formats.aimat_suffix()}')
                    p.save(fpath=fpath, force_overwrite=force_overwrite)

        else:
            for j, pattern in enumerate(self.patterns):
                fpath = os.path.join(dirpath, f'pattern_{j}.{Formats.aimat_suffix()}')
                pattern.save(fpath=fpath, force_overwrite=force_overwrite)

    @classmethod
    def load(cls, dirpath : str, strict : bool = False, suffixes : Optional[list[str]] = None, csv_orientation : Optional[Orientation] = None) -> PatternDB:
        dirpath = os.path.normpath(path=dirpath)
        if not os.path.isdir(dirpath):
            raise ValueError(f"Given path {dirpath} is not a directory")

        data_fpaths = Formats.get_xrd_fpaths(dirpath=dirpath, selected_suffixes=suffixes)
        if len(data_fpaths) == 0:
            raise ValueError(f"No data files matching suffixes {suffixes} found in directory {dirpath}")

        fpath_dict = {}
        failed_files = set()
        patterns : list[XrdPattern] = []
        def extract(xrd_fpath : str) -> list[XrdPatternData]:
            return parser.extract(fpath=xrd_fpath, csv_orientation=csv_orientation)

        for fpath in TrackedCollection(data_fpaths):
            new_patterns = [XrdPattern(**info.to_dict()) for info in extract(fpath)]
            patterns += new_patterns
            fpath_dict[fpath] = new_patterns

            for info in extract(xrd_fpath=fpath):
                try:
                    p = XrdPattern(**info.to_dict())
                    if not fpath in fpath_dict:
                        fpath_dict[fpath] = []
                    fpath_dict[fpath].append(p)
                except Exception as e:
                    failed_files.add(fpath)
                    patterdb_logger.warning(msg=f"Could not import pattern from file {fpath}:\n- Reason: \"{e}\"\n")
                    if strict:
                        raise e

        return PatternDB(patterns=patterns, fpath_dict=fpath_dict, failed_files=failed_files)

    # -------------------------------------------
    # operations

    def __add__(self, other):
        return PatternDB.merge(dbs=[self, other])

    @classmethod
    def merge(cls, dbs : list[PatternDB]):
        patterns = []
        failed_files = set()
        fpath_dict = {}
        for db in dbs:
            patterns += db.patterns
            failed_files.update(db.failed_files)
            fpath_dict.update(db.fpath_dict)

        return PatternDB(patterns=patterns, failed_files=failed_files, fpath_dict=fpath_dict)


    def set_xray(self, xray_info : XRayInfo):
        for p in self.patterns:
            p.powder_experiment.xray_info = xray_info

    # -------------------------------------------
    # attributes

    def __eq__(self, other):
        if not isinstance(other, PatternDB):
            return False
        if len(self.patterns) != len(other.patterns):
            return False
        for self_pattern, other_pattern in zip(self.patterns, other.patterns):
            if self_pattern != other_pattern:
                return False
        return True

    def get_parsing_report(self) -> DatabaseReport:
        return DatabaseReport(data_dirpath=self.name, failed_files=self.failed_files, fpath_dict=self.fpath_dict)

    def plot_all(self):
        batch_size = 32

        j = 0
        while j < len(self.patterns):
            pattern_batch = self.patterns[j:j + batch_size]
            for k,p in enumerate(pattern_batch):
                p.metadata.filename = p.metadata.filename or f'pattern_{j+k}'
            multiplot(patterns=pattern_batch)
            j += batch_size

            user_input = input(f'Press enter to continue or q to quit')
            if user_input.lower() == 'q':
                break


    def show_histograms(self, save_fpath : Optional[str] = None):
        fig = plt.figure(figsize=(12,8))

        figure = gridspec.GridSpec(nrows=2, ncols=1, figure=fig, hspace=0.5)
        upper_half = figure[0].subgridspec(1, 3)
        ax2 = fig.add_subplot(upper_half[:, :])
        self.define_spg_ax(patterns=self.patterns, ax=ax2)
        
        lower_half = figure[1].subgridspec(1, 2)
        ax3 = fig.add_subplot(lower_half[:, 0])
        self.define_recorded_angles_ax(patterns=self.patterns, ax=ax3)

        lower_half_right = lower_half[1].subgridspec(nrows=3, ncols=3)
        ax4 = fig.add_subplot(lower_half_right[1:, :2]) # scaatter
        ax5 = fig.add_subplot(lower_half_right[:1, :2], sharex=ax4)  # Above
        ax6 = fig.add_subplot(lower_half_right[1:, 2:], sharey=ax4)  # Right
        self.define_density_ax(patterns=self.patterns, density_ax=ax4, top_marginal=ax5, right_marginal=ax6)

        if save_fpath:
            plt.savefig(save_fpath)
        plt.show()

    @staticmethod
    def define_spg_ax(patterns : list[XrdPattern], ax : Axes):
        keys, counts = get_counts(patterns=patterns, attr='primary_phase.spacegroup')
        keys, counts = keys[:30], counts[:30]

        spgs = [int(k) for k in keys]
        spg_formulas = [f'${SpacegroupConverter.to_formula(spg, mathmode=True)}$' for spg in spgs]
        ax.bar(spg_formulas, counts)
        ax.tick_params(labelbottom=True, labelleft=True)  # Enable labels
        ax.set_title(f'(a)')
        ax.set_ylabel(f'No. patterns')
        ax.set_xticklabels(spg_formulas, rotation=90)
        
    @staticmethod
    def define_recorded_angles_ax(patterns : list[XrdPattern], ax : Axes):
        values = get_valid_values(patterns=patterns, attr='angular_resolution')
        ax.set_title(f'(b)')
        ax.hist(values, bins=30, range=(0,0.1))
        ax.set_xlabel(r'Angular resolution $\Delta(2\theta)$ [$^\circ$]')
        ax.set_yscale('log')
        ax.set_ylabel(f'No. patterns')

    @staticmethod
    def define_density_ax(patterns : list[XrdPattern], density_ax : Axes, top_marginal : Axes, right_marginal : Axes):
        start_data = get_valid_values(patterns=patterns, attr='startval')
        end_data = get_valid_values(patterns=patterns, attr='endval')
        start_angle_range = (0,60)
        end_angle_range = (0,180)

        sns.kdeplot(x=start_data, y=end_data, fill=True, ax=density_ax)
        # noinspection PyTypeChecker
        # density_ax.hist2d(start_data,end_data, bins=20, range=[list(start_angle_range),list(end_angle_range)])
        density_ax.set_xlabel(r'Smallest recorded $2\theta$ value [$^\circ$]')
        density_ax.set_ylabel(r'Largest recorded $2\theta$ value [$^\circ$]')
        density_ax.set_xlim(start_angle_range)
        density_ax.set_ylim(end_angle_range)

        top_marginal.hist(start_data, bins=range(*start_angle_range))
        top_marginal.set_title(f'(c)')
        top_marginal.set_yscale('log')
        top_marginal.tick_params(axis="x", labelbottom=False)

        right_marginal.hist(end_data, bins=range(*end_angle_range,5), orientation='horizontal')
        right_marginal.set_xscale('log')
        right_marginal.tick_params(axis="y", labelleft=False)



