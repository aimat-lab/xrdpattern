from __future__ import annotations
from typing import Optional


class XrdFormat:

    @classmethod
    def from_suffix(cls, suffix : str) -> Optional[XrdFormat]:
        return suffix_to_format_dict.get(suffix)

    def __init__(self, name : str, suffix :str):
        self.name : str = name
        self.suffix : str = suffix


class Formats:
    bruker_raw = XrdFormat("bruker_raw", "raw")
    bruker_spc = XrdFormat("bruker_spc", "spc")
    canberra_cnf = XrdFormat("canberra_cnf", "cnf")
    canberra_mca = XrdFormat("canberra_mca", "mca")
    chiplot = XrdFormat("chiplot", "chiplot")
    cpi = XrdFormat("cpi", "cpi")
    csv = XrdFormat("csv", "csv")
    dbws = XrdFormat("dbws", "dbw")
    pdcif = XrdFormat("pdcif", "cif")
    philips_raw = XrdFormat("philips_raw", "rd")
    philips_udf = XrdFormat("philips_udf", "udf")
    riet7 = XrdFormat("riet7", "dat")
    rigaku_dat = XrdFormat("rigaku_dat", "dat")
    specsxy = XrdFormat("specsxy", "specsxy")
    spectra = XrdFormat("spectra", "spectra")
    text = XrdFormat("text", "txt")
    uxd = XrdFormat("uxd", "uxd")
    vamas = XrdFormat("vamas", "vms")
    winspec_spe = XrdFormat("winspec_spe", "spe")
    xfit_xdd = XrdFormat("xfit_xdd", "xdd")
    xrdml = XrdFormat("xrdml", "xrdml")
    xsyg = XrdFormat("xsyg", "xsyg")
    aimat_json = XrdFormat("ajson","json")



suffix_to_format_dict = {xrd_format.suffix : xrd_format for xrd_format in Formats.__dict__.values() if isinstance(xrd_format, XrdFormat)}
allowed_suffix_types = [xrd_format.suffix for xrd_format in Formats.__dict__.values() if isinstance(xrd_format, XrdFormat)]

class FormatSelector:
    @classmethod
    def make_allow_all(cls):
        return cls(allow_all=True)

    def __init__(self, allow_all : bool = False, format_list : Optional[list[str]] = None):
        self.format_list : Optional[list[str]] = format_list
        self.allow_all : bool = allow_all

        if not self.allow_all and format_list is None:
            raise ValueError("If allow_all is False, format_list must be provided")


    def is_allowed(self, the_format : str) -> bool:
        if self.allow_all:
            return True
        else:
            return the_format in self.format_list
