class packet:
    def __init__(self, id:int, data:dict, data_code:int):
        self.id = id
        self.data = data
        self.data_code = data_code

    def set_id(self, id:int):
        self.id = id

    def set_data(self, data:dict):
        self.data = data

    def set_data_code(self, data_code:int):
        self.data_code = data_code