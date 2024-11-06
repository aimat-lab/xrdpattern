from __future__ import annotations
from dataclasses import dataclass
from holytools.fsys import SaveManager
from xrdpattern.parsing.stoe import StoeParser

@dataclass
class XrdFormat:
    name : str
    suffix : str


class Formats:
    bruker_raw = XrdFormat("bruker_raw", "raw")
    stoe_raw = XrdFormat("stoe_raw", 'raw')
    bruker_spc = XrdFormat("bruker_spc", "spc")
    canberra_cnf = XrdFormat("canberra_cnf", "cnf")
    canberra_mca = XrdFormat("canberra_mca", "mca")
    chiplot = XrdFormat("chiplot", "chi")
    cpi = XrdFormat("cpi", "cpi")
    csv = XrdFormat("csv", "csv")
    dbws = XrdFormat("dbws", "dbw")
    pdcif = XrdFormat("pdcif", "cif")
    philips_rd = XrdFormat("philips_rd", "rd")
    philips_udf = XrdFormat("philips_udf", "udf")
    riet7 = XrdFormat("riet7", "dat")
    rigaku_dat = XrdFormat("rigaku_dat", "dat")
    text = XrdFormat("text", "txt")
    uxd = XrdFormat("uxd", "uxd")
    xfit_xdd = XrdFormat("xfit_xdd", "xdd")
    xrdml = XrdFormat("xrdml", "xrdml")
    xsyg = XrdFormat("xsyg", "xsyg")
    aimat_xrdpattern = XrdFormat("aimat", "json")
    cif = XrdFormat('cif', 'cif')


    @classmethod
    def get_datafile_suffixes(cls):
        return [xrd_format.suffix for xrd_format in cls.get_all_formats() if not xrd_format.suffix in [Formats.aimat_xrdpattern.suffix, "csv"]]

    @classmethod
    def get_allowed_suffixes(cls) -> list[str]:
        return [xrd_format.suffix for xrd_format in cls.get_all_formats()]

    @classmethod
    def get_all_formats(cls) -> list[XrdFormat]:
        return [xrd_format for xrd_format in cls.__dict__.values() if isinstance(xrd_format, XrdFormat)]

    @classmethod
    def get_format(cls, fpath : str) -> XrdFormat:
        suffix = SaveManager.get_suffix(fpath)
        if suffix == 'raw':
            xrd_format = Formats.stoe_raw if StoeParser.is_stoe(fpath) else Formats.bruker_raw
        else:
            suffix_to_format_map = {xrd_format.suffix : xrd_format for xrd_format in cls.get_all_formats()}
            xrd_format = suffix_to_format_map.get(suffix)
            if not xrd_format:
                raise ValueError(f"Invalid suffix {suffix}")

        return xrd_format


