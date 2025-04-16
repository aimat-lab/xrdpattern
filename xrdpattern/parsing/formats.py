from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from xrdpattern.parsing.xylib import get_xylib_repr

from xrdpattern.parsing.path_tools import PathTools
from .stoe import StoeParser


# -------------------------------------------


@dataclass
class XrdFormat:
    name : str
    suffixes : list[str]

class Formats:
    bruker_raw = XrdFormat("bruker_raw", ["raw"])
    bruker_spc = XrdFormat("bruker_spc", ["spc"])
    canberra_cnf = XrdFormat("canberra_cnf", ["cnf"])
    canberra_mca = XrdFormat("canberra_mca", ["mca"])
    chiplot = XrdFormat("chiplot", ["chi"])
    cpi = XrdFormat("cpi", ["cpi"])
    dbws = XrdFormat("dbws", ["dbw"])
    philips_rd = XrdFormat("philips_rd", ["rd"])
    philips_udf = XrdFormat("philips_udf", ["udf"])
    riet7 = XrdFormat("riet7", ["dat"])
    rigaku_dat = XrdFormat("rigaku_dat", ["dat"])
    text = XrdFormat("text", ["txt", 'xy'])
    uxd = XrdFormat("uxd", ["uxd"])
    xfit_xdd = XrdFormat("xfit_xdd", ["xdd"])
    xrdml = XrdFormat("xrdml", ["xrdml"])
    xsyg = XrdFormat("xsyg", ["xsyg"])

    plaintext_dat = XrdFormat("column_dat", ["dat"])
    pdcif = XrdFormat("pdCIF", ["cif"])
    aimat_xrdpattern = XrdFormat("aimat", ['json'])
    stoe_raw = XrdFormat("stoe_raw", ['raw'])
    csv = XrdFormat("csv", ["csv", "xlsx"])

    @classmethod
    def aimat_suffix(cls) -> str:
        return cls.aimat_xrdpattern.suffixes[0]

    @classmethod
    def get_xylib_formats(cls):
        formatsOne = [cls.bruker_raw, cls.bruker_spc, cls.canberra_cnf, cls.canberra_mca, cls.chiplot, cls.cpi]
        formatsTwo = [cls.dbws, cls.philips_rd, cls.philips_udf, cls.riet7, cls.rigaku_dat, cls.text]
        formatsTrhee = [cls.uxd, cls.xfit_xdd, cls.xrdml, cls.xsyg]
        return formatsOne + formatsTwo + formatsTrhee

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
        suffix = PathTools.get_suffix(fpath)
        if suffix == 'raw':
            return Formats.stoe_raw if cls.is_stoe(fpath) else Formats.bruker_raw
        if suffix == 'dat':
            if Formats.is_rigaku_dat(fpath):
                return Formats.rigaku_dat
            elif Formats.is_riet_dat(fpath):
                return Formats.riet7
            else:
                return Formats.plaintext_dat

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
    def is_rigaku_dat(cls, fpath : str) -> bool:
        try:
            get_xylib_repr(fpath=fpath,format_name=Formats.rigaku_dat.name)
            is_rigaku_dat = True
        except:
            is_rigaku_dat = False
        return is_rigaku_dat

    @classmethod
    def is_riet_dat(cls, fpath : str) -> bool:
        try:
            get_xylib_repr(fpath=fpath,format_name=Formats.riet7.name)
            is_riet_dat = True
        except:
            is_riet_dat = False
        return is_riet_dat

    @staticmethod
    def get_xrd_fpaths(dirpath: str, selected_suffixes : Optional[list[str]]) -> list[str]:
        if selected_suffixes is None:
            selected_suffixes = Formats.get_all_suffixes()
        selected_suffixes = [x.replace('.', '') for x in selected_suffixes]

        subfile_paths = PathTools.get_subfile_fpaths(dirpath=dirpath)
        data_fpaths = [p for p in subfile_paths if PathTools.get_suffix(fpath=p) in selected_suffixes]

        return data_fpaths



if __name__ == "__main__":
    # tha_format = Formats.get_format(fpath='/home/daniel/aimat/opXRD/raw/zhang_cao_0/data/caobin_pxrd_xy/C/xy.txt')
    # print(tha_format)

    file_foramt = Formats.get_format(fpath='/home/daniel/aimat/data/opXRD/processed/sutter-fella_kodalle_0/data/CIGS_Pvsk_GIWAXS/Dat-Samples/Sample_04-2-PVD/PVD.dat')
    print(file_foramt)