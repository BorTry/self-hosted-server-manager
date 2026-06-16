import re

from .named_entries import project_name, network, service, volume
from .named_entries_base import named_entry_base

class grouping:
    NAME_CLASS_MAPPING = {
        "name": project_name,
        "services": service,
        "networks": network,
        "volumes": volume
    }

    __slots__ = ("grouping_type", "data_block", "grouping_entries")

    def __init__(self, grouping_type:str, data_block:str=None):
        self.grouping_type = grouping_type
        self.data_block = data_block

        self.grouping_entries = {}

        if data_block is not None:
            self._extract_data()

            self.data_block = None

    def _extract_data(self):
        if (self.grouping_type == "name"):
            self.grouping_entries["name"] = project_name(self.data_block.split(":")[1].strip())
            return

        _section_groups_from_data(self.grouping_entries, self.data_block, r"(?m)^ {2}(\w+)")

        for entry in self.grouping_entries:
            tmp = {}
            _section_groups_from_data(tmp, self.grouping_entries[entry], r"(?m)^ {4}(\w+)")

            self.grouping_entries[entry] = grouping.NAME_CLASS_MAPPING[self.grouping_type](name=entry,**tmp)

    def __repr__(self):
        final_str = f"{self.grouping_type}: {"\n" if self.grouping_type != "name" else ""}"
        
        for entry_name in self.grouping_entries:
            final_str += f"{self.grouping_entries[entry_name]!r}\n"

        return final_str
    
    def __iter__(self):
        return iter(self.grouping_entries)

    def __setitem__(self, key, value):
        self.grouping_entries[key] = value

    def __getitem__(self, key) -> named_entry_base|project_name:
        if not (key in self.grouping_entries): return None
        return self.grouping_entries[key]

    def __delitem__(self, key):
        del self.grouping_entries[key]

    def add_entry(self, new_entry:named_entry_base|project_name):
        self.grouping_entries[new_entry.name] = new_entry

def _section_groups_from_data(grouping_entries:dict, data:str, pattern:str):
    group_entries = re.finditer(pattern, data)

    prev = None

    for entry in group_entries:
        if prev == None:
            prev = entry
            continue

        grouping_entries[prev.group(0).strip()] = data[prev.end()+1:entry.start()]
        prev = entry
    
    if prev is not None:
        grouping_entries[prev.group(0).strip()] = data[prev.end()+1:]