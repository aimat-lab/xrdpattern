from __future__ import annotations

import json
from typing import  get_type_hints
from typing import get_origin, get_args, Union
from types import NoneType

# -------------------------------------------

class SerializableDataclass:

    def to_str(self) -> str:
        return json.dumps(self.to_json())

    @classmethod
    def from_str(cls, json_str : str):
        return cls.from_json(json_dict=json.loads(json_str))

    def to_json(self) -> dict:
        return {attr : self.get_json_entry(obj=value) for attr, value in self.__dict__.items()}

    @classmethod
    def from_json(cls, json_dict : dict) -> SerializableDataclass:
        obj = cls.__new__(cls)
        attr_types = get_type_hints(cls)

        for key, value in json_dict.items():
            attr_type = attr_types.get(key)
            if is_optional_serializable(the_type=attr_type):
                if not value is None:
                    setattr(obj, key, cls.from_json(json_dict=value))
            elif issubclass(attr_type, SerializableDataclass):
                setattr(obj, key, cls.from_json(json_dict=value))
            else:
                setattr(obj, key, value)
        return obj


    @staticmethod
    def get_json_entry(obj):
        is_composite = isinstance(obj, SerializableDataclass)
        if is_composite:
            return obj.to_json()
        return obj


def is_optional_serializable(the_type : type):
    is_optional_ser = False
    if get_origin(the_type) is Union:
        is_optional_ser = any([issubclass(subtype,SerializableDataclass) for subtype in get_args(the_type)])
    return is_optional_ser


def get_core_type(the_type):
    if get_origin(the_type) is Union:
        types = get_args(the_type)

        core_types = [t for t in types if not t is NoneType]
        print(core_types)
        if len(core_types) == 1:
            return core_types[0]

    raise TypeError("Type must be of the form Optional[type]")

