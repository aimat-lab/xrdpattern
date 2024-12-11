from __future__ import annotations

import os
import random
import seaborn as sns

from dataclasses import dataclass
from typing import Optional

from matplotlib import pyplot as plt
from spglib import spglib

from holytools.logging import LoggerFactory
from holytools.userIO import TrackedCollection
import matplotlib.gridspec as gridspec
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
    failed_files : list[str]
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
        failed_files = []
        patterns : list[XrdPattern] = []
        def extract(xrd_fpath : str) -> list[XrdPatternData]:
            return parser.extract(fpath=xrd_fpath, csv_orientation=csv_orientation)

        for fpath in TrackedCollection(data_fpaths):
            try:
                new_patterns = [XrdPattern(**info.to_dict()) for info in extract(fpath)]
                patterns += new_patterns
                fpath_dict[fpath] = new_patterns
            except Exception as e:
                failed_files.append(fpath)
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
        failed_files = []
        fpath_dict = {}
        for db in dbs:
            patterns += db.patterns
            failed_files += db.failed_files
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
        attrs = ['primary_phase.spacegroup', 'num_entries', 'startval', 'endval']
        fig = plt.figure(figsize=(12,8))

        figure = gridspec.GridSpec(nrows=2, ncols=1, figure=fig, hspace=0.5)
        upper_half = figure[0].subgridspec(1, 3)
        ax2 = fig.add_subplot(upper_half[:, :])

        keys, counts = get_counts(patterns=self.patterns, attr=attrs[0])
        keys, counts = keys[:30], counts[:30]

        spgs = [spglib.get_spacegroup_type(hall_number=int(k)) for k in keys]
        spg_ints = [f'${spg["international_full"]}$' for spg in spgs]
        ax2.bar(spg_ints, counts)
        ax2.tick_params(labelbottom=True, labelleft=True)  # Enable labels
        ax2.set_xlabel(f'Spacegroup')
        ax2.set_title(f'(a)')
        ax2.set_ylabel(f'No. patterns')
        ax2.set_xticklabels(spg_ints, rotation=90)

        lower_half = figure[1].subgridspec(1, 2)
        ax3 = fig.add_subplot(lower_half[:, 0])
        bins = range(0, 10000, 100)
        values = get_valid_values(patterns=self.patterns, attr=attrs[1])
        ax3.set_title(f'(b)')
        ax3.hist(values, bins=bins)
        ax3.set_xlabel(f'Recorded angles')
        ax3.set_ylabel(f'No. patterns')


        start_data = get_valid_values(patterns=self.patterns, attr=attrs[2])
        end_data = get_valid_values(patterns=self.patterns, attr=attrs[3])

        lower_half_right = lower_half[1].subgridspec(nrows=3, ncols=3)
        ax4 = fig.add_subplot(lower_half_right[1:, :2]) # scaatter
        ax4.set_xlabel(r'First recorded $2\theta$ value')
        ax4.set_ylabel(r'Final recorded $2\theta$ value')

        ax5 = fig.add_subplot(lower_half_right[:1, :2],sharex=ax4) # Above
        ax5.set_title(f'(c)')
        ax5.set_yscale('log')
        ax6 = fig.add_subplot(lower_half_right[1:, 2:],sharey=ax4) # Right

        ax5.hist(start_data, bins=range(0,30))
        ax6.hist(end_data, bins=range(30,180,5), orientation='horizontal')
        ax6.set_xscale('log')

        # start_data = random.sample(start_data, 1000)
        # end_data = random.sample(end_data, 1000)
        sns.kdeplot(x=start_data, y=end_data, fill=True, color='red', ax=ax4)
        ax6.tick_params(axis="y", labelleft=False)
        ax5.tick_params(axis="x", labelbottom=False)

        if save_fpath:
            plt.savefig(save_fpath)
        plt.show()
