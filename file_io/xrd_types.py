from typing import Optional

class XrdFormat:
    def __init__(self, name : str, suffix :str):
        self.name : str = name
        self.suffix : str = suffix


class XYLibOption:
    def __init__(self, input_path : str, output_path : str, input_type : Optional[XrdFormat] = None):
        self.INPUT_FILE : str = input_path
        self.OUTPUT_PATH : str = output_path
        self.INPUT_TYPE : Optional[XrdFormat] = input_type


class Formats:
    bruker_raw = XrdFormat("bruker_raw", ".raw")
    bruker_spc = XrdFormat("bruker_spc", ".spc")
    canberra_cnf = XrdFormat("canberra_cnf", ".cnf")
    canberra_mca = XrdFormat("canberra_mca", ".mca")
    chiplot = XrdFormat("chiplot", ".chiplot")
    cpi = XrdFormat("cpi", ".cpi")
    csv = XrdFormat("csv", ".csv")
    dbws = XrdFormat("dbws", ".dbw")
    pdcif = XrdFormat("pdcif", ".cif")
    philips_raw = XrdFormat("philips_raw", ".rd")
    philips_udf = XrdFormat("philips_udf", ".udf")
    riet7 = XrdFormat("riet7", ".dat")
    rigaku_dat = XrdFormat("rigaku_dat", ".dat")
    specsxy = XrdFormat("specsxy", ".specsxy")
    spectra = XrdFormat("spectra", ".spectra")
    text = XrdFormat("text", ".txt")
    uxd = XrdFormat("uxd", ".uxd")
    vamas = XrdFormat("vamas", ".vms")
    winspec_spe = XrdFormat("winspec_spe", ".spe")
    xfit_xdd = XrdFormat("xfit_xdd", ".xdd")
    xrdml = XrdFormat("xrdml", ".xrdml")
    xsyg = XrdFormat("xsyg", ".xsyg")


file_endings = [xrd_format.suffix for xrd_format in Formats.__dict__.values() if isinstance(xrd_format, XrdFormat)]
