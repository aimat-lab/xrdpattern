import json

import numpy as np
import requests
from CrystalStructure.crystal import CrystalStructure
from xrdpattern.core import PowderExperiment, Artifacts, PowderSample
from xrdpattern.pattern import XrdPattern

with open('/home/daniel/Drive/data/workspace/extracted_data.json', 'r') as f:
    content = f.read()

the_dict = json.loads(content)
print('done reading json')
base_url = 'https://www.crystallography.net/cod'

for cod_id, value in the_dict.items():
    try:
        num = cod_id.split('/')[-1]
        request_url = f'{base_url}/{num}.cif'
        cif_content = requests.get(url=request_url).content.decode()
        spg_keyword = f'_space_group_IT_number'
        spg = None
        for line in cif_content.split(f'\n'):
            if spg_keyword in line:
                _, spg = line.split()
        if not spg is None:
            spg = int(spg)

        structure = CrystalStructure.from_cif(cif_content=cif_content)
        structure.spacegroup = spg
        artifacts = Artifacts(primary_wavelength=None, secondary_wavelength=None, secondary_to_primary=None)
        powder_sample = PowderSample(structure, crystallite_size=None, temp_in_celcius=None)

        label = PowderExperiment(powder=PowderSample(crystal_structure=structure, crystallite_size=None, temp_in_celcius=None),
                                 artifacts=Artifacts(None, None, None), is_simulated=False)
        two_thetas = np.array(value['x'])
        intensities = np.array(value['y'])
        name = f"COD_{value['id']}"

        pattern = XrdPattern(two_theta_values=two_thetas, intensities=intensities, label=label, name=name)
        fpath = f'/home/daniel/Drive/data/workspace/opxrd/cod/{name}.json'
        pattern.save(fpath=fpath, force_overwrite=True)
        print(f'Successfully parsed structure number {value["id"]} and saved file at {fpath}')

    except BaseException as e:
        print(f'Failed to extract COD pattern due to error {e}')


if __name__ == "__main__":
    print(f'done')