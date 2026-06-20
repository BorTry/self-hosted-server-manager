from typing import Any

class packet:
    __slots__ = ("id", "data", "code")
    
    def __init__(self, id:int, data:Any, code:int):
        self.id = id
        self.data = data
        self.code = code

    def set_id(self, id:int):
        self.id = id

    def set_data(self, data:Any):
        self.data = data

    def set_data_code(self, code:int):
        self.code = code

    def __repr__(self):
        return f"\n\tid: {self.id}\n\tdata: {self.data}\n\tcode: {self.code}"