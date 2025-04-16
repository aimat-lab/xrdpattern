from __future__ import annotations

import dataclasses
import os
from abc import abstractmethod
from dataclasses import dataclass
from datetime import datetime, date, time
from decimal import Decimal
from enum import Enum
from types import NoneType
from typing import Optional
from typing import get_type_hints, get_origin, get_args, Union

import orjson

# ---------------------------------------------------------------------

class Serializable:
    @abstractmethod
    def to_str(self) -> str:
        pass

    @classmethod
    @abstractmethod
    def from_str(cls, s: str):
        pass

    def save(self, fpath : str, force_overwrite : bool = False) -> str:
        fpath = os.path.abspath(path=fpath)
        dirpath = os.path.dirname(fpath)
        os.makedirs(dirpath, exist_ok=True)
        full_name = os.path.basename(fpath)
        non_suffixname = full_name.split('.')[0]
        suffix = get_suffix(fpath)

        if os.path.isfile(fpath) and not force_overwrite:
            fpath = get_free_path(save_dirpath=dirpath, name=non_suffixname, suffix=suffix, start_index=1)
            print(f'Warning: File already exists at specified filepath. Saving to {fpath} instead.')

        with open(fpath, 'w') as f:
            f.write(self.to_str())

        return fpath

    @classmethod
    def load(cls, fpath : str):
        with open(fpath, 'r') as f:
            str_data = f.read()
        return cls.from_str(str_data)


def get_suffix(fpath) -> Optional[str]:
    parts = fpath.split('.')
    if len(parts) == 1:
        return None
    else:
        return parts[-1]


def get_free_path(save_dirpath : str, name : str, suffix : Optional[str] = None, start_index : int = 0) -> str:
    if suffix:
        if not suffix.startswith('.'):
            suffix = f'.{suffix}'

    def get_path(index : int = start_index):
        conditional_suffix = '' if suffix is None else f'{suffix}'
        conditional_index = f'_{index}' if not index is None else ''
        return os.path.join(save_dirpath, f'{name}{conditional_index}{conditional_suffix}')

    fpath = get_path()
    current_index = 0
    while os.path.isfile(path=fpath) or os.path.isdir(fpath):
        current_index += 1
        fpath = get_path(index=current_index)
    return fpath


BasicSerializable = (bool | int | float | str | Serializable | Decimal | datetime | date | time | Enum | None)

@dataclass
class JsonDataclass(Serializable):
    """Enables serialization of dataclasses with following attributes:
    - Basic serializable types as defined above:
        - Serialization: get_basic_entry()
        - Deserialization: make_basic()
    - Lists, tuples or dicts of basic serializable types"""

    def __init__(self, *args, **kwargs):
        _, __ = args, kwargs
        if not dataclasses.is_dataclass(self):
            raise TypeError(f'{self.__class__} must be a dataclass to be Jsonifyable')

    def to_str(self) -> str:
        defined_fields = set([f.name for f in dataclasses.fields(self) if f.init])
        json_dict = {}
        for attr, value in [(attr, value) for attr, value in self.__dict__.items() if attr in defined_fields]:
            if isinstance(value, list):
                entry = [self.get_basic_entry(x) for x in value]
            elif isinstance(value, tuple):
                entry = tuple([self.get_basic_entry(x) for x in value])
            elif isinstance(value, dict):
                key_list = [self.get_basic_entry(k) for k in value.keys()]
                value_list = [self.get_basic_entry(v) for v in value.values()]
                entry = (key_list, value_list)
            else:
                entry = self.get_basic_entry(obj=value)
            json_dict[attr] = entry

        return orjson.dumps(json_dict).decode("utf-8")

    @classmethod
    def from_str(cls, json_str: str):
        if not dataclasses.is_dataclass(cls):
            raise TypeError(f'{cls} is not a dataclass. from_json can only be used with dataclasses')

        json_dict = orjson.loads(json_str)
        type_hints = get_type_hints(cls)
        init_dict = {}
        for key, value in json_dict.items():
            dtype = type_hints.get(key)
            if TypeAnalzer.is_optional(dtype) and value is None:
                init_dict[key] = None
                continue
            if dtype is None:
                continue

            dtype = TypeAnalzer.strip_nonetype(dtype)
            origin = get_origin(dtype)
            if origin == list:
                item_type = TypeAnalzer.get_inner_types(dtype)[0]
                restored_value = [cls.make_basic(basic_cls=item_type, s=x) for x in value]
            elif origin == tuple:
                item_types = TypeAnalzer.get_inner_types(dtype)
                restored_value = tuple(
                    [cls.make_basic(basic_cls=item_type, s=s) for item_type, s in zip(item_types, value)])
            elif origin == dict or dtype == dict:
                key_type, value_type = TypeAnalzer.get_inner_types(dtype)
                key_list = [cls.make_basic(basic_cls=key_type, s=x) for x in value[0]]
                value_list = [cls.make_basic(basic_cls=value_type, s=x) for x in value[1]]
                restored_value = {key: value for key, value in zip(key_list, value_list)}
            else:
                restored_value = cls.make_basic(basic_cls=dtype, s=value)
            init_dict[key] = restored_value

        return cls(**init_dict)

    @staticmethod
    def get_basic_entry(obj) -> (str | int | NoneType):
        if not isinstance(obj, BasicSerializable):
            raise TypeError(f'Object {obj} is not a basic serializable type')

        if obj is None:
            entry = None
        elif isinstance(obj, Serializable):
            entry = obj.to_str()
        elif isinstance(obj, Enum):
            entry = obj.name
        elif isinstance(obj, float) and obj != obj:
            entry = 'nan'
        elif isinstance(obj, bool):
            entry = bool(int(obj))
        else:
            entry = str(obj)
        return entry

    @staticmethod
    def make_basic(basic_cls, s: str):
        castable_classes = ['str', 'int', 'float', 'bool', 'Decimal', 'UUID', 'Path']
        converters = {
            datetime: datetime.fromisoformat,
            date: date.fromisoformat,
            time: time.fromisoformat,
        }

        if basic_cls in converters:
            instance = converters[basic_cls](s)
        elif basic_cls.__name__ in castable_classes:
            instance = basic_cls(s)
        elif issubclass(basic_cls, Enum):
            instance = basic_cls[s]
        elif issubclass(basic_cls, Serializable):
            instance = basic_cls.from_str(s)
        elif basic_cls == NoneType:
            instance = None
        else:
            raise TypeError(f'Unsupported type {basic_cls}')
        return instance


class TypeAnalzer:
    @staticmethod
    def is_optional(dtype):
        origin = get_origin(dtype)
        if origin is Union:
            return NoneType in get_args(dtype)
        else:
            return False

    # noinspection DuplicatedCode
    @staticmethod
    def strip_nonetype(dtype: type) -> type:
        origin = get_origin(dtype)
        if origin is Union:
            types = get_args(dtype)
            not_none_types = [t for t in types if not t is NoneType]
            if len(not_none_types) == 1:
                core_type = not_none_types[0]
            else:
                raise ValueError(f'Union dtype {dtype} has more than one core dtype')
        else:
            core_type = dtype
        return core_type

    @staticmethod
    def get_inner_types(dtype: type) -> tuple:
        inner_dtypes = get_args(dtype)
        return inner_dtypes
