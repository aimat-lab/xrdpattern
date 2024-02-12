from __future__ import annotations

import copy
import os
from abc import abstractmethod
from typing import Optional
from .xrd_types import allowed_suffix_types

# -------------------------------------------

def find_all_parsable_files(dir_path : str) -> list[str]:
    if not os.path.isdir(dir_path):
        raise ValueError(f"Given path {dir_path} is not a directory")
    root_node = XrdFsysNode(path=dir_path)
    root_node.init_fsys()

    return root_node.get_xrd_file_des()


class XrdFsysNode:
    def __init__(self, path : str):
        self.path : str = path
        self.name : str = os.path.basename(path)

        self.potential_xrd_children : list = []
        self.potential_xrd_des : list = []
        self.xrd_node_des : list =[]

        self.fsys_dict : Optional[dict] = None
        self.is_xrd_relevant : Optional[bool] = None


    def init_fsys(self):
        self.initialize_potential_des()
        self.find_xrd_relevant_nodes()


    def initialize_potential_des(self):
        for name in self.get_all_potential_sub():
            child = self.add_child(name=name)
            child.fsys_dict = self.fsys_dict[name]
            self.potential_xrd_children += [child]

        self.potential_xrd_des = copy.copy(self.potential_xrd_children)
        for child in self.potential_xrd_children:
            child.init_fsys()
            self.potential_xrd_des += child.potential_xrd_des


    def find_xrd_relevant_nodes(self):
        for fsys_des in self.potential_xrd_des:
            self.xrd_node_des += [fsys_des] if fsys_des.get_is_xrd_relevant() else []

    @abstractmethod
    def add_child(self, name : str):
        pass

    # -------------------------------------------
    # get

    def get_all_potential_sub(self) -> list[str]:
        fsys_dict = self.get_fsys_dict()
        sub_paths = [os.path.join(self.path, name) for name in list(fsys_dict.keys())]
        potentially_relevant = lambda path : path_is_xrd_file(path) or os.path.isdir(path)

        relevant_paths = [path for path in sub_paths if potentially_relevant(path)]
        relevant_names = [os.path.basename(path) for path in relevant_paths]

        return relevant_names

    def get_fsys_dict(self) -> dict:
        if self.fsys_dict is None:
            self.fsys_dict = make_fsys_dict(root_dir=self.path)

        return self.fsys_dict

    def get_is_xrd_relevant(self) -> bool:
        if not self.is_xrd_relevant is None:
            return self.is_xrd_relevant

        if self.get_is_file():
            self.is_xrd_relevant = self.get_is_xrd_file()

        else:
            self.is_xrd_relevant = any([child.get_is_xrd_relevant() for child in self.potential_xrd_children])

        return self.is_xrd_relevant

    def get_is_file(self) -> bool:
        return os.path.isfile(self.path)

    def get_is_xrd_file(self) -> bool:
        return path_is_xrd_file(path=self.path)

    def get_xrd_file_des(self) -> list[str]:
        return [node for node in self.xrd_node_des if node.get_is_xrd_file()]


def path_is_xrd_file(path : str):
    is_file = os.path.isfile(path)
    is_xrd_format = any([path.endswith(the_format) for the_format in allowed_suffix_types])
    return is_file and is_xrd_format


def make_fsys_dict(root_dir : str) -> dict:
    file_structure = {}
    for root, dirs, files in os.walk(root_dir, followlinks=True):
        relative_path = root.replace(root_dir, '').lstrip(os.sep)
        current_level = file_structure

        parts = relative_path.split(os.sep)
        for part in parts:
            if part:
                current_level = current_level.setdefault(part, {})

        for file in files:
            current_level[file] = None

    return file_structure


