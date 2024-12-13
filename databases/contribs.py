import os
import shutil
import tempfile
from typing import Optional

from databases.processors.opxrd import OpXRDProcessor
from xrdpattern.parsing import Orientation


class ContributionProcessor(OpXRDProcessor):
    def parse_INT(self):
        db0 = self.get_pattern_db(input_dirname='breitung_schweidler_0', selected_suffixes=['raw'])
        db1 = self.get_pattern_db(input_dirname='breitung_schweidler_1', selected_suffixes=['raw'])
        merged = db0 + db1
        merged.save(dirpath=os.path.join(self.final_dirpath, 'INT'))

    def parse_CNRS(self):
        db = self.get_pattern_db(input_dirname='coudert_hardiagon_0', selected_suffixes=['json'])
        db.save(dirpath=os.path.join(self.final_dirpath, 'CNRS'))


    def parse_USC(self):
        db0 = self.get_pattern_db(input_dirname='hodge_alwen_0', xray_info=self.cu_xray)
        db1 = self.get_pattern_db(input_dirname='hodge_alwen_1', xray_info=self.cu_xray)
        merged = db0 + db1
        merged.save(dirpath=os.path.join(self.final_dirpath, 'USC'))

    def parse_LBNL(self):
        def get_contribution(dirname : str, selected_suffixes : Optional[list[str]] = None):
            return self.get_pattern_db(input_dirname=dirname, csv_orientation=Orientation.HORIZONTAL,
                                       selected_suffixes=selected_suffixes, strict=True)

        perovskite_db =  get_contribution(dirname='sutter-fella_singh_0')
        perovskite_db += get_contribution(dirname='sutter-fella_kodalle_0', selected_suffixes=['dat','csv'])
        perovskite_db += get_contribution(dirname='sutter-fella_abdelsamie_0')
        perovskite_db.save(dirpath=os.path.join(self.final_dirpath, 'LBNL_perovskite'), label_groups=True)

        uio_db = get_contribution(dirname='sutter-fella_hu_0')
        uio_db.save(dirpath=os.path.join(self.final_dirpath, 'LBNL_uio'), label_groups=True)

        mn_sb_db = get_contribution(dirname='sutter-fella_heymans_0', selected_suffixes=['xlsx'])
        mn_sb_db.save(dirpath=os.path.join(self.final_dirpath, 'LBNL_mn_sb_o'), label_groups=True)

    def parse_EMPA(self):
        db0 = self.get_pattern_db(input_dirname='siol_wieczorek_0', xray_info=self.cu_xray)
        db1 = self.get_pattern_db(input_dirname='siol_zhuk_0', xray_info=self.cu_xray)
        merged = db0 + db1
        merged.save(dirpath=os.path.join(self.final_dirpath, 'EMPA'))

    def parse_IKFT(self):
        db = self.get_pattern_db(input_dirname='wolf_wolf_0', xray_info=self.cu_xray)
        db.save(dirpath=os.path.join(self.final_dirpath, 'IKFT'))

    def parse_HKUST(self):
        db = self.get_pattern_db(input_dirname='zhang_cao_0', use_cif_labels=True, selected_suffixes=['txt'], xray_info=self.cu_xray)
        db.save(dirpath=os.path.join(self.final_dirpath, 'HKUST'))

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
    processor.parse_LBNL()
    # processor.parse_all()
    # processor.prepare_zips()