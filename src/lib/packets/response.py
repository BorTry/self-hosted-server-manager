from .packet_types import packet_types
from .packet import packet
from ..json_decoder_encoder import register

from typing import Any

@register
class response(packet):
    __slots__ = ("_type", )

    def __init__(self, id:int, data:Any, code:int):
        super().__init__(id, data, code)

        self._type = packet_types.RESPONSE