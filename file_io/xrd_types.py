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
