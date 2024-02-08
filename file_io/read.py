import os.path
from xyconv import convert_file
from xyconv import list_supported_formats
from typing import Optional
# from logger import Logger


class XrdFormat:
    def __init__(self, name : str, suffix :str):
        self.name : str = name
        self.suffix : str = suffix

class XYLibOption:
    def __init__(self, input_path : str, output_path : str):
        self.INPUT_PATH : str = input_path
        self.OUTPUT_PATH : str = output_path
        self.s : bool = True


BRUKER_RAW_V1 = XrdFormat("Siemens/Bruker diffract v1 raw files", ".raw")
BRUKER_RAW_V2 = XrdFormat("Siemens/Bruker diffract v2 raw files", ".raw")
BRUKER_RAW_V4 = XrdFormat("Siemens/Bruker v4 raw files", ".raw")
PDCIF = XrdFormat("pdCIF format files", ".cif")
PHILIPS_RD = XrdFormat("Philips RD files", ".rd")
PHILIPS_UDF = XrdFormat("Philips UDF files", ".udf")
XRDML = XrdFormat("PANalytical XRDML files", ".xrdml")
UXD = XrdFormat("UXD files", ".uxd")
RIGAKU_DAT = XrdFormat("Rigaku dat files", ".dat")
VAMAS = XrdFormat("VAMAS files", ".vms")
GSAS = XrdFormat("GSAS files", ".gss")
TEXT = XrdFormat("Text files", ".txt")
WIN_SPEC_SPE = XrdFormat("Princeton Instruments WinSpec SPE files", ".spe")
SIERAY_CPI = XrdFormat("Sietronics Sieray CPI files", ".cpi")
DBWS = XrdFormat("DBWS data files", ".dbw")
CANBERRA_MCA = XrdFormat("Canberra MCA files", ".mca")
CANBERRA_CNF = XrdFormat("Canberra CNF file", ".cnf")
XFIT_XDD = XrdFormat("XFIT XDD files", ".xdd")
RIET7_ILL_D1A5_PSI_DMC = XrdFormat("RIET7 / ILL_D1A5 / PSI_DMC files", ".dat")
SPECTRA = XrdFormat("Spectra Omicron XPS data example", ".1")
SPECSLAB2_XY = XrdFormat("SpecsLab2 xy-file", ".xy")
XSYG = XrdFormat("xsyg example file", ".xsyg")


def convert(input_path : str, output_dir : str, output_format : XrdFormat, name : Optional[None] = None):
    if not os.path.isfile(input_path):
        raise ValueError(f"File {input_path} does not exist")

    try:
        input_name = os.path.basename(input_path).split('.')[0] if name is None else name
        output_path =  os.path.join(output_dir, f"{input_name}{output_format.suffix}")
        option = XYLibOption(input_path=input_path, output_path=output_path)
        convert_file(opt=option)

    except Exception as e:
        raise ValueError(f"Error converting file {input_path} to {output_format.name}. Error: {str(e)}")


if __name__ == "__main__":
    list_supported_formats()