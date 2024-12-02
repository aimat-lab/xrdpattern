from databases.processors.opxrd import ContributionProcessor
from xrdpattern.parsing import Orientation


class OpXRDProcessor(ContributionProcessor):
    def parse_INT(self):
        self.process(dirname='breitung_schweidler_0', selected_suffixes=['raw'])
        self.process(dirname='breitung_schweidler_1', selected_suffixes=['raw'])

    def parse_CNRS(self):
        self.process(dirname='coudert_hardiagon_0', selected_suffixes=['json'])

    def parse_USC(self):
        self.process(dirname='hodge_alwen_0', xray_info=self.cu_xray)
        self.process(dirname='hodge_alwen_1', xray_info=self.cu_xray)

    def parse_LBNL(self):
        self.process(dirname='sutter-fella_heymans_0', selected_suffixes=['xlsx'], csv_orientation=Orientation.VERTICAL, label_groups=True)

    def parse_EMPA(self):
        self.process(dirname='siol_wieczorek_0', xray_info=self.cu_xray)
        self.process(dirname='siol_zhuk_0', xray_info=self.cu_xray)

    def parse_IKFT(self):
        self.process(dirname='wolf_wolf_0', xray_info=self.cu_xray)

    def parse_HKUST(self):
        self.process(dirname='zhang_cao_0', use_cif_labels=True,selected_suffixes=['txt'], xray_info=self.cu_xray)


if __name__ == "__main__":
    processor = OpXRDProcessor(root_dirpath='/home/daniel/aimat/data/opXRD/')
    processor.parse_LBNL()