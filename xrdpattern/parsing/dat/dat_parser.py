import numpy as np

from xrdpattern.xrd import XrdData, XrayInfo


class DatParser:
    def extract_multi(self, fpath : str) -> list[XrdData]:
        data = self.get_data_dict(fpath=fpath)
        x,y = self.get_xy_data(data_dict=data)
        x = np.array(x)
        y = np.array(y)

        img_indices = self.image_indices(img_list=data['imagenum'])
        img_indices.append(len(x))
        image_lengths = [img_indices[k+1] - img_indices[k] for k in range(len(img_indices)-1)]

        patterns = []
        for l in image_lengths:
            pattern_angles = x[:l]
            pattern_intensities = y[:l]
            x,y = x[l:], y[l:]

            new_pattern = XrdData.make_unlabeled(two_theta_values=pattern_angles, intensities=pattern_intensities)
            new_pattern.powder_experiment.xray_info = XrayInfo.copper_xray()
            patterns.append(new_pattern)

        return patterns


    @staticmethod
    def get_data_dict(fpath: str) -> dict[str, list[str]]:
        with open(fpath, 'r') as f:
            content = f.read()
            lines = content.split('\n')
        entries = [line.split() for line in lines if not line.strip() == '']
        headers = entries[0]
        data = entries[1:]

        data_dict = {}
        for j, header in enumerate(headers):
            data_dict[header] = [entry[j] for entry in data]
        return data_dict

    @staticmethod
    def image_indices(img_list : list[str]) -> list[int]:
        img_list = [int(s) for s in img_list]

        current_frame = 0
        indices = []
        for k, frame_num in enumerate(img_list):
            if frame_num == current_frame:
                indices.append(k)
                current_frame += 1

        return indices

    @staticmethod
    def get_xy_data(data_dict : dict[str, list[str]]) -> (list[float], list[float]):
        angles = [float(val) for val in data_dict['twotheta']]
        intensities = [float(val) for val in data_dict['intensity']]
        return angles, intensities


if __name__ == "__main__":
    dat_parser = DatParser()
    dat_parser.extract_multi(fpath='/home/daniel/aimat/data/opXRD/processed/sutter-fella_kodalle_0/data/CIGS_Pvsk_GIWAXS/Dat-Samples/Sample_04-2-PVD/PVD.dat')