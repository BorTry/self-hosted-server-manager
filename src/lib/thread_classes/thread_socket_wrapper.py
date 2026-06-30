from .thread_wrapper import thread_wrapper
from .thread_data_handler import thread_data_handler

from ..packets import packet, response, batch, batch_header, packet_types
from ..json_decoder_encoder import decoder, encoder
from ..server_codes import Server_codes 

from socket import socket, AF_INET, SOCK_DGRAM
from json import dumps, loads

from typing import Callable, Any
from threading import Event
from math import ceil

BUFFER_SIZE = 2048
CONNECTION_TYPE = (AF_INET, SOCK_DGRAM)

class thread_socket_wrapper(thread_wrapper):
    __slots__ = ("address", "target_address", "socket")

    def __init__(self, target:Callable=None, init:Callable=None, on_close:Callable=None, address:tuple[str, int]=None, target_address:tuple[str, int]=None, data_handler:thread_data_handler=None, terminate_signal:Event=None, name:str="thread", sleeptime:float=0.0):
        self.target_address = target_address
        self.address = address

        self.socket = socket(*CONNECTION_TYPE)

        if (address):
            self.socket.bind(address)

        self.socket.settimeout(0.25)

        super().__init__(target, init, on_close, terminate_signal, name, data_handler, sleeptime)

    def send(self, data_packet:packet|None, code:int=None, target:tuple[str, int]=None):
        target_address = target or self.target_address

        if (not target_address):
            raise ValueError("Target address not defined, in class or function")
        
        if code:
            data_packet.set_data_code(code)

        if data_packet._type == packet_types.BATCH or data_packet._type == packet_types.BATCH_HEADER:
            self.socket.sendto(_encode(data_packet), target_address)
            return

        encoded_data = dumps(data_packet.data)
        data_size = len(encoded_data)

        if data_size > BUFFER_SIZE:
            self._chunk_and_send_data(data_packet, data_size, target_address)
        else:
            self.socket.sendto(_encode(data_packet), target_address)

    def recv(self):       
        try:
            new_data, address = self.socket.recvfrom(BUFFER_SIZE)

            decoded_data = _decode(new_data)
            
            if decoded_data._type == packet_types.BATCH_HEADER:
                return self._recieve_batches(decoded_data, address)
            else:
                return decoded_data, address

        except TimeoutError: 
            return None, None

        except Exception as e:
            self.print(e)
            return None, None

    def send_recv(self, data:packet|None, code:int=None) -> response|None:
        self.send(data_packet=data, code=code)
        new_data, _ = self.recv()

        return new_data

    def terminate(self):
        super().terminate()

        if (self.socket.fileno() != -1):
            self.socket.close()

    def get_new_instance(self):
        return thread_socket_wrapper(self.target, self.init, self.address, self.target_address, self.terminate_signal, self.name, self.sleep_time)

    def _recieve_batches(self, batch_header_packet:batch_header, address:tuple[str, int]):
        BATCH_BUFFER = []

        self.send(response(None, "", Server_codes.OK), target=address) # confirmation

        for i in range(batch_header_packet.total_batches):
            batch_data, _ = self.socket.recvfrom(BUFFER_SIZE)
            decoded_batch_data = _decode(batch_data)

            if (decoded_batch_data.sequence != i):
                self.print(f"Something went wrong, got sequnce number {decoded_batch_data.sequence} at place {i}")

            BATCH_BUFFER.append(decoded_batch_data.data)
        self.socket.recvfrom(BUFFER_SIZE)

        return response(batch_header_packet.id, self._dechunk_data(BATCH_BUFFER), batch_header_packet.code), address

    def _chunk_and_send_data(self, data_packet:packet, data_size:int, target_address:tuple[str, int]):
        max_data_size = ceil(BUFFER_SIZE * 0.8)
        total_batches = ceil(data_size / max_data_size) # "done" confirmation packet

        self.send_recv(batch_header(data_packet.id, data_packet.code, total_batches)) # ask to open for a batch

        str_data = data_packet.data

        for i in range(total_batches):
            start = max_data_size * i
            end =  max_data_size * (i+1)

            data_segment = str_data[start:end]

            self.send(batch(data_segment, i))
        self.send(response(data_packet.id, "", Server_codes.OK), target=target_address)

    def _dechunk_data(self, batched_data):
        return "".join(batched_data)

def _encode(data: Any) -> bytes:
    return dumps(data, cls=encoder).encode("utf-8")

def _decode(data: bytes) -> Any:
    return loads(data.decode("utf-8"), cls=decoder)