from .formats import XrdFormat
from dataclasses import dataclass
from typing import Optional


@dataclass
class ParsingOptions:
    format_hint : Optional[XrdFormat] = None
    is_q_values : bool = False