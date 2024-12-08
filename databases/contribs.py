import os
import shutil
import tempfile
from typing import Optional

from databases.processors.opxrd import OpXRDProcessor
from xrdpattern.parsing import Orientation


class ContributionProcessor(OpXRDProcessor):
    def parse_INT(self):
        self.process(input_dirname='breitung_schweidler_0', selected_suffixes=['raw'], output_dirname='INT_0')
        self.process(input_dirname='breitung_schweidler_1', selected_suffixes=['raw'], output_dirname='INT_1')

    def parse_CNRS(self):
        self.process(input_dirname='coudert_hardiagon_0', selected_suffixes=['json'], output_dirname='CNRS_0')

    def parse_USC(self):
        self.process(input_dirname='hodge_alwen_0', xray_info=self.cu_xray, output_dirname='USC_0')
        self.process(input_dirname='hodge_alwen_1', xray_info=self.cu_xray, output_dirname='USC_1')

    def parse_LBNL(self):
        def parse_csv_contribution(dirname : str,num : int, selected_suffixes : Optional[list[str]] = None):
            output_dirname = f'LBNL_{num}'
            self.process(input_dirname=dirname, csv_orientation=Orientation.VERTICAL, label_groups=True, selected_suffixes=selected_suffixes, output_dirname=output_dirname)

        parse_csv_contribution(dirname='sutter-fella_heymans_0', selected_suffixes=['xlsx'], num=0)
        parse_csv_contribution(dirname='sutter-fella_abdelsamie_0', num=1)
        parse_csv_contribution(dirname='sutter-fella_hu_0', num=2)
        parse_csv_contribution(dirname='sutter-fella_kodalle_0', selected_suffixes=['dat','csv'],num=3)
        parse_csv_contribution(dirname='sutter-fella_singh_0', num=4)

    def parse_EMPA(self):
        self.process(input_dirname='siol_wieczorek_0', xray_info=self.cu_xray, output_dirname='EMPA_0')
        self.process(input_dirname='siol_zhuk_0', xray_info=self.cu_xray, output_dirname='EMPA_1')

    def parse_IKFT(self):
        self.process(input_dirname='wolf_wolf_0', xray_info=self.cu_xray, output_dirname='IKFT_0')

    def parse_HKUST(self):
        self.process(input_dirname='zhang_cao_0', use_cif_labels=True, selected_suffixes=['txt'], xray_info=self.cu_xray, output_dirname='HKUST_0')

    def prepare_zips(self):
        dir_content_names = os.listdir(self.final_dirpath)
        dir_content_paths = [os.path.join(self.final_dirpath, name) for name in dir_content_names]
        dirpaths = [d for d in dir_content_paths if os.path.isdir(d)]

        in_situ_dirs = [d for d in dirpaths if 'LBNL' in d]
        non_situ_dirs = [d for d in dirpaths if d not in in_situ_dirs]

        print(f'In situ dirs: {in_situ_dirs}')
        print(f'Non situ dirs: {non_situ_dirs}')

        in_situ_fpath = os.path.join(self.final_dirpath, 'opxrd_in_situ.zip')
        self._zip_dirs(in_situ_dirs, output_fpath=in_situ_fpath)

        non_situ_fpath = os.path.join(self.final_dirpath, 'opxrd.zip')
        self._zip_dirs(non_situ_dirs, output_fpath=non_situ_fpath)

    @staticmethod
    def _zip_dirs(dirpaths : list[str], output_fpath : str):
        if len(dirpaths) == 0:
            raise ValueError('No directories to zip')

        tmp_dir = tempfile.mktemp()
        for d in dirpaths:
            print(f'Copying {d} to {tmp_dir}')
            tmp_dirpath = os.path.join(tmp_dir, os.path.basename(d))
            shutil.copytree(d,tmp_dirpath)
        print(f'Zipping {tmp_dir} to {output_fpath}')
        parts = output_fpath.split('.')[:-1]
        output_fpath = '.'.join(parts)
        shutil.make_archive(base_name=output_fpath, format='zip', root_dir=tmp_dir)


if __name__ == "__main__":
    processor = ContributionProcessor(root_dirpath='/home/daniel/aimat/data/opXRD/')
    processor.parse_all()
    processor.prepare_zips()