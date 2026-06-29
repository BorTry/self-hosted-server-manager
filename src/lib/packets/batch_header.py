from .packet_types import packet_types
from ..json_decoder_encoder import register

@register
class batch_header:
    __slots__ = ( "_type", "id", "total_batches", "code")
    
    def __init__(self, id:int, code:int, total_batches:int):
        self.id = id
        self.total_batches = total_batches
        self.code = code

        self._type = packet_types.BATCH_HEADER

    def __repr__(self):
        return f"\n\tid: {self.id}\n\tcode: {self.code}\n\ttotal_batches: {self.total_batches}"