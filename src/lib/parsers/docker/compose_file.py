import re

from .sub_classes.grouping import grouping
from .sub_classes.named_entries import network, service, volume

class compose_file:
    __slots__ = ("file_path", "top_level_entries", "name", "services", "volumes", "networks")

    def __init__(self, file_path):
        self.file_path = file_path
        self.top_level_entries = []

        self._get_groups()

    def _get_groups(self):
        with open(self.file_path, "r") as file:
            whole_file = file.read()

        text_groups = re.finditer(r"(?m)^(\w+)", whole_file)
        prev = None
        blocks = {}

        for text in text_groups:
            if prev == None:
                prev = text
                continue

            blocks[prev.group(0)] = whole_file[prev.start():text.start()]
            prev = text

        blocks[prev.group(0)] = whole_file[prev.start():]

        for block in blocks:
            setattr(self, block, grouping(block, blocks[block]))
            self.top_level_entries.append(block)

    def __repr__(self):
        final_str = ""

        for att in self.top_level_entries:
            final_str += f"{getattr(self, att, "")!r}"

        return final_str

    def add_service(self, new_service:service):
        if (not ("services" in self.top_level_entries)):
            self.services = grouping("services")
            self.top_level_entries.append("services")
        self.services.add_entry(new_service)

    def add_network(self, new_network:network):
        if (not ("networks" in self.top_level_entries)):
            self.networks = grouping("networks")
            self.top_level_entries.append("networks")
        self.networks.add_entry(new_network)

    def add_volume(self, new_volume:volume):
        if (not ("volumes" in self.top_level_entries)):
            self.volumes = grouping("volumes")
            self.top_level_entries.append("volumes")
        self.volumes.add_entry(new_volume)

    def write_to_file(self):
        with open(self.file_path, "w") as file:
            file.write(f"{self!r}")