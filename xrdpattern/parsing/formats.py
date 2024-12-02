from __future__ import annotations
from dataclasses import dataclass
from holytools.fsys import SaveManager
from .stoe import StoeParser

# -------------------------------------------


@dataclass
class XrdFormat:
    name : str
    suffixes : list[str]

class Formats:
    bruker_raw = XrdFormat("bruker_raw", ["raw"])
    stoe_raw = XrdFormat("stoe_raw", ['raw'])
    bruker_spc = XrdFormat("bruker_spc", ["spc"])
    canberra_cnf = XrdFormat("canberra_cnf", ["cnf"])
    canberra_mca = XrdFormat("canberra_mca", ["mca"])
    chiplot = XrdFormat("chiplot", ["chi"])
    cpi = XrdFormat("cpi", ["cpi"])
    csv = XrdFormat("csv", ["csv", "xlsx"])
    dbws = XrdFormat("dbws", ["dbw"])
    pdcif = XrdFormat("pdCIF", ["cif"])
    philips_rd = XrdFormat("philips_rd", ["rd"])
    philips_udf = XrdFormat("philips_udf", ["udf"])
    riet7 = XrdFormat("riet7", ["dat"])
    rigaku_dat = XrdFormat("rigaku_dat", ["dat"])
    text = XrdFormat("text", ["txt", 'xy'])
    uxd = XrdFormat("uxd", ["uxd"])
    xfit_xdd = XrdFormat("xfit_xdd", ["xdd"])
    xrdml = XrdFormat("xrdml", ["xrdml"])
    xsyg = XrdFormat("xsyg", ["xsyg"])
    aimat_xrdpattern = XrdFormat("aimat", ['json'])

    @classmethod
    def aimat_suffix(cls) -> str:
        return cls.aimat_xrdpattern.suffixes[0]

    @classmethod
    def get_datafile_formats(cls):
        return [f for f in cls.get_all_formats() if not f in [Formats.aimat_xrdpattern, Formats.csv]]

    @classmethod
    def get_all_suffixes(cls) -> list[str]:
        all_suffixes = []
        for f in cls.get_all_formats():
            all_suffixes += f.suffixes
        return all_suffixes

    @classmethod
    def get_all_formats(cls) -> list[XrdFormat]:
        return [xrd_format for xrd_format in cls.__dict__.values() if isinstance(xrd_format, XrdFormat)]

    @classmethod
    def get_format(cls, fpath : str) -> XrdFormat:
        suffix = SaveManager.get_suffix(fpath)
        if suffix == 'raw':
            return Formats.stoe_raw if cls.is_stoe(fpath) else Formats.bruker_raw


        suffix_to_format_map = {}
        for f in cls.get_all_formats():
            for s in f.suffixes:
                suffix_to_format_map[s] = f
        xrd_format = suffix_to_format_map.get(suffix)
        if not xrd_format:
            raise ValueError(f"Invalid suffix {suffix}")

        return xrd_format

    @classmethod
    def is_stoe(cls, fpath : str) -> bool:
        try:
            reader = StoeParser()
            reader.read(fpath=fpath)
            angle_start, angle_end = reader.angle_start.get_value(), reader.angle_end.get_value()
            num_entries = reader.num_entries.get_value()

            angles_ok = 0 < angle_start < angle_end < 180
            entries_ok = isinstance(num_entries, int) and 0 < num_entries < 10**6
            is_stoe = angles_ok and entries_ok

        except:
            is_stoe = False

        return is_stoe

    @classmethod
    def is_binary_dat(cls, fpath : str) -> bool:
        try:
            get_xylib_repr(fpath=fpath,format_hint=Formats.rigaku_dat)
            is_rigaku_dat = True
        except:
            is_rigaku_dat = False

        try:
            get_xylib_repr(fpath=fpath,format_hint=Formats.riet7)
            is_riet_dat = True
        except:
            is_riet_dat = False

        return is_rigaku_dat or is_riet_dat



if __name__ == "__main__":
    # tha_format = Formats.get_format(fpath='/home/daniel/aimat/opXRD/raw/zhang_cao_0/data/caobin_pxrd_xy/C/xy.txt')
    # print(tha_format)

    is_binary = Formats.is_binary_dat(fpath='/home/daniel/aimat/data/opXRD/processed/sutter-fella_kodalle_0/data/CIGS_Pvsk_GIWAXS/Dat-Samples/Sample_04-2-PVD/PVD.dat')
    print(is_binary)