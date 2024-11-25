import json
import os

import requests

from holytools.fsys import SaveManager
from xrdpattern.pattern import XrdPattern


# -------------------------------------------------

def write_cod(json_fpath : str, out_dirpath : str):
    with open(json_fpath, 'r') as f:
        content = f.read()

    the_dict = json.loads(content)
    print('done reading json')

    for cod_id in the_dict.keys():
        num = cod_id.split('/')[-1]
        fname = f"COD_{num}"
        save_fpath = os.path.join(out_dirpath, f'{fname}.json')
        try:
            pattern = parse_cod_cif(num=num)
            pattern.save(fpath=save_fpath, force_overwrite=True)
            print(f'Successfully parsed structure number {num} and saved file at {save_fpath}')

        except BaseException as e:
            print(f'Failed to extract COD pattern {num} due to error {e}')


def parse_cod_cif(num : int) -> XrdPattern:
    base_url = 'https://www.crystallography.net/cod'
    cif_request_url = f'{base_url}/{num}.cif'
    cif_content = requests.get(url=cif_request_url).content.decode()

    try:
        hkl_request_url = f'{base_url}/{num}.hkl'
        hkl_content = requests.get(url=hkl_request_url).content.decode()
        loops = hkl_content.split(f'loop_')
        xfields = ["_pd_proc_2theta_corrected", "_pd_meas_2theta_scan", "_pd_meas_2theta"]

        for l in loops:
            l = l.strip()
            if any([x in l for x in xfields]):
                cif_content += f'loop_\n{l}'
    except:
        pass

    temp_fpath = SaveManager.get_tmp_fpath(suffix='.cif')
    with open(temp_fpath, 'w') as f:
        f.write(cif_content)

    return XrdPattern.load(fpath=temp_fpath)


if __name__ == "__main__":
    cod_int = 1508528
    pattern = parse_cod_cif(num=cod_int)
    pattern.save(fpath=f'./thisjson.json', force_overwrite=True)

    # j_fpath = '/home/daniel/aimat/opXRD/raw/coudert_hardiagon_0/data/extracted_data.json'
    # the_out_dirpath = '/home/daniel/aimat/opXRD/raw/coudert_hardiagon_0/data/'
    # write_cod(json_fpath=j_fpath, out_dirpath=the_out_dirpath)
    # print(f'done')