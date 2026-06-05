from .packet_types import packet_types
from .packet import packet

from typing import Any


class request(packet):
    def __init__(self, id:int, data:dict, data_code:int):
        super().__init__(id, data, data_code)

        self.type = packet_types.REQUEST