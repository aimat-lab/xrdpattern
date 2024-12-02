from typing import Optional

from xrdpattern.crystal import CrystalPhase


def read_file(fpath: str) -> str:
    with open(fpath, 'r') as file:
        cif_content = file.read()
    return cif_content


def safe_cif_read(cif_content: str) -> Optional[CrystalPhase]:
    try:
        extracted_phase = CrystalPhase.from_cif(cif_content)
    except:
        extracted_phase = None
    return extracted_phase
