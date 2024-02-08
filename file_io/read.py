import os.path
from uuid import uuid4
from tempfile import TemporaryDirectory

from .xyconv import convert_file
from .xyconv import list_supported_formats


class XrdFormat:
    def __init__(self, name : str, suffix :str):
        self.name : str = name
        self.suffix : str = suffix

class XYLibOption:
    def __init__(self, input_path : str, output_path : str):
        self.INPUT_FILE : str = input_path
        self.OUTPUT_PATH : str = output_path
        self.s : bool = True

class Formats:
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


file_endings = [xrd_format.suffix for xrd_format in Formats.__dict__.values() if isinstance(xrd_format, XrdFormat)]


def get_repr(input_path : str, xrd_format : XrdFormat) -> str:
    if not os.path.isfile(input_path):
        raise ValueError(f"File {input_path} does not exist")

    input_format = '.' + input_path.split('.')[-1]
    if not input_format in file_endings:
        raise ValueError(f"File {input_path} is not a supported format")

    try:
        with TemporaryDirectory() as output_dir:
            file_name = uuid4()
            output_path =  os.path.join(output_dir, f"{file_name}{xrd_format.suffix}")
            option = XYLibOption(input_path=input_path, output_path=output_path)
            convert_file(opt=option)
            return get_file_contents(filepath=output_path)

    except Exception as e:
        raise ValueError(f"Error converting file {input_path} to {xrd_format.name}. Error: {str(e)}")


def get_file_contents(filepath : str) -> str:
    if not os.path.isfile(filepath):
        raise ValueError(f"File {filepath} does not exist")

    with open(filepath, "r") as file:
        return file.read()


if __name__ == "__main__":
    list_supported_formats()