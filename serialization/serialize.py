from __future__ import annotations
from datetime import datetime
import json
from typing import  get_type_hints
from typing import get_origin, get_args, Union
from types import NoneType

# -------------------------------------------

class SerializableDataclass:
    @classmethod
    def from_str(cls, json_str: str):
        json_dict = json.loads(json_str, object_hook=cls.json_decode)
        return cls.from_json(json_dict=json_dict)

    def to_str(self) -> str:
        return json.dumps(self.to_json(), default=self.json_encode)

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

    @staticmethod
    def json_decode(json_dict):
        for key, value in json_dict.items():
            if isinstance(value, str):
                try:
                    json_dict[key] = datetime.fromisoformat(value)
                except ValueError:
                    pass
        return json_dict

    @staticmethod
    def json_encode(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return json.JSONEncoder().default(obj)



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



if __name__ == "__main__":
    from dataclasses import dataclass
    from typing import Optional

    @dataclass
    class MySerializable(SerializableDataclass):
        name: str
        value: int
        example_date : datetime = datetime(year=2000, month=1, day=13)
        nested: Optional[SerializableDataclass] = None

    def abc():
        pass

    inner_obj = MySerializable('nested', 2)
    test_obj = MySerializable('test', 1, nested=inner_obj)

    inner_str = inner_obj.to_str()
    outer_obj_str = test_obj.to_str()

    new_obj = MySerializable.from_str(json_str=inner_str)
    new_outer_obj = MySerializable.from_str(json_str=outer_obj_str)
    print(new_obj.__dict__)
    print(new_outer_obj.__dict__)
