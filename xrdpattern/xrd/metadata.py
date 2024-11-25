from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from holytools.abstract import JsonDataclass


@dataclass
class OriginMetadata(JsonDataclass):
    filename : Optional[str] = None
    institution : Optional[str] = None
    contributor_name : Optional[str] = None
    file_format : Optional[str] = None
    measurement_date: Optional[str] = None
    tags: list[str] = field(default_factory=list)

    def __eq__(self, other : OriginMetadata):
        s1, s2 = self.to_str(), other.to_str()
        return s1 == s2
