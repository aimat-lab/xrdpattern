from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from holytools.abstract import JsonDataclass
import pkg_resources

def get_library_version(library_name):
    return pkg_resources.get_distribution(library_name).version


@dataclass
class Metadata(JsonDataclass):
    filename: Optional[str] = None
    institution: Optional[str] = None
    contributor_name: Optional[str] = None
    original_file_format: Optional[str] = None
    measurement_date: Optional[str] = None
    tags: list[str] = field(default_factory=list)
    xrdpattern_version: str = field(default_factory=lambda: get_library_version('xrdpattern'))

    def __eq__(self, other : Metadata):
        s1, s2 = self.to_str(), other.to_str()
        return s1 == s2

    def remove_filename(self):
        self.filename = None


if __name__ == "__main__":
    metadata = Metadata()
    print(metadata)