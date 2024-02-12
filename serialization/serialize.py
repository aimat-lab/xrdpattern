from __future__ import annotations
import json
from typing import  get_type_hints
from typing import get_origin, get_args, Union
from types import NoneType
from abc import abstractmethod

# -------------------------------------------

class SerializableDataclass:

    def to_json(self) -> dict:
        return {attr : self.get_json_entry(obj=value) for attr, value in self.__dict__.items()}

    @classmethod
    def from_json(cls, json_dict : dict) -> SerializableDataclass:
        obj = cls.__new__(cls)
        attr_types = get_type_hints(cls)

        for key, value in json_dict.items():
            # print(key, value)
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


#
# if __name__ == "__main__":
#     @dataclass
#     class MySerializable(SerializableDataclass):
#         name : str
#         value : int
#         # this_stuff : datetime = datetime(year=2022, month=1, day=13)
#         nested : Optional[SerializableDataclass] = None
#
#     inner_obj = MySerializable('nested', 2)
#     test_obj = MySerializable('test', 1, nested=inner_obj)
#
#     test_json_dict = inner_obj.to_json()
#     test_json_dict2 = test_obj.to_json()
#
#     json_str = json.dumps(test_json_dict2)
#     print(json_str)
#
#     new_json = json.loads(json_str)
#
#     new_obj = MySerializable.from_json(json_dict=new_json)
#     print(new_obj.__dict__)
