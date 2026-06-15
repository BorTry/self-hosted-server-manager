from abc import ABC
import re

from .constants import SPACING

class named_entry_base(ABC):
    TESTS = {
        "is_string": lambda x: bool(re.match(r"^[^\n+](\/|\S+)", x)),
        "is_list": lambda x: bool(re.match(r"^\s+\-", x)),
    }

    __slots__ = ("name", )

    def __init__(self, name, **kwargs):
        self.name = name

        for kwarg in kwargs:
            setattr(self, kwarg, kwargs[kwarg])

        self._iterative_structuring()

    def __repr__(self):
        final_str = f"{SPACING}{self.name}:\n"

        for att in self.__slots__:
            if att == "name": continue

            value = getattr(self, att, None)

            if not value: continue

            str_representation = ""

            match (value):
                case list():
                    str_representation = _turn_list_to_str(value)
                case dict():
                    str_representation = _turn_dict_to_str(value)
                case str():
                    str_representation = value + "\n"

            final_str += f"{SPACING*2}{att}: {str_representation}"

        return final_str
    
    def _iterative_structuring(self):
        # separates lists, dicts and strings
        for att in self.__slots__:
            if att == "name": continue

            value = getattr(self, att, None)

            if (not value): continue

            if named_entry_base.TESTS["is_string"](value):
                setattr(self, att, value.strip())
            elif named_entry_base.TESTS["is_list"](value):
                setattr(self, att, _create_list(value))
            else:
                setattr(self, att, _create_dict(value))

def _turn_list_to_str(array):
    final_str = "\n"
    
    for value in array:
        final_str += f"{SPACING*3}- {value}\n"

    return final_str 

def _turn_dict_to_str(dictionary, depth=0):
    final_str = "\n"
    
    for key in dictionary:
        if type(dictionary[key]) is dict:
            final_str += _turn_dict_to_str(dictionary[key], depth + 1)
        else:
            final_str += f"{SPACING*(3+depth)}{key}: {dictionary[key]}\n"

    return final_str

def _create_list(value):
    return re.findall(r"- (\S+)", value)

def _create_dict(value):
    dic = {}

    all_values = re.finditer(r"(\S+)\: (\S+)", value)

    for entry in all_values:
        dic[entry.group(1)] = entry.group(2)

    return dic