from .packet_types import packet_types
from ..json_decoder_encoder import register

from typing import Any

@register
class batch:
    __slots__ = ("_type", "data", "sequence")

    def __init__(self, data:Any, sequence:int):
        self.data = data
        self.sequence = sequence

        self._type = packet_types.BATCH

    def __repr__(self):
        return f"\n\tsequence_number: {self.sequence}\n\tdata: {self.data}"