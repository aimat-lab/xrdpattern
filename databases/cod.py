import json
import os

import requests

from holytools.fsys import SaveManager
from xrdpattern.parsing import MasterParser

# -------------------------------------------------

def write_cod(json_fpath : str, out_dirpath : str):
    with open(json_fpath, 'r') as f:
        content = f.read()

    the_dict = json.loads(content)
    print('done reading json')
    base_url = 'https://www.crystallography.net/cod'

    for cod_id, value in the_dict.items():
        num = cod_id.split('/')[-1]
        request_url = f'{base_url}/{num}.cif'
        cif_content = requests.get(url=request_url).content.decode()

        try:
            temp_fpath = SaveManager.get_tmp_fpath(suffix='.cif')
            with open(temp_fpath, 'w') as f:
                f.write(cif_content)

            parser = MasterParser()
            pattern = parser.extract(fpath=temp_fpath)[0]

            fname = f"COD_{value['id']}"
            save_fpath = os.path.join(out_dirpath, f'{fname}.json')
            pattern.save(fpath=save_fpath, force_overwrite=True)
            print(f'Successfully parsed structure number {value["id"]} and saved file at {save_fpath}')

        except BaseException as e:
            print(f'Failed to extract COD pattern {num} due to error {e}')

if __name__ == "__main__":
    j_fpath = '/home/daniel/aimat/opXRD/raw/coudert_hardiagon_0/data/extracted_data.json'
    the_out_dirpath = '/home/daniel/aimat/opXRD/raw/coudert_hardiagon_0/data/'
    write_cod(json_fpath=j_fpath, out_dirpath=the_out_dirpath)
    print(f'done')