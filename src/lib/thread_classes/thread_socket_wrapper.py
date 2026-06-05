from socket import socket, AF_INET, SOCK_DGRAM
from json import dumps, loads

from typing import Callable, Any
from threading import Event

from .thread_wrapper import thread_wrapper
from .thread_data_handler import thread_data_handler

from ..packets import packet

BUFFER_SIZE = 1024
CONNECTION_TYPE = (AF_INET, SOCK_DGRAM)

class thread_socket_wrapper(thread_wrapper):
    __slots__ = ("address", "target_address", "socket")

    def __init__(self, target:Callable=None, init:Callable=None, address:tuple[str, int]=None, target_address:tuple[str, int]=None, data_handler:thread_data_handler=None, terminate_signal:Event=None, name:str="thread", sleeptime:float=0.0):
        if (not address):
            raise Exception("Socket thread needs an address to bind to")

        self.target_address = target_address # Only given if a socket thread needs to send and wait for an answer
        self.address = address

        self.socket = socket(*CONNECTION_TYPE)
        self.socket.bind(address)

        self.socket.settimeout(0.25)

        super().__init__(target, init, terminate_signal, name, data_handler, sleeptime)

    def send(self, data:packet|None, code:int=None, target:tuple[str, int]=None):
        target_address = target or self.target_address

        if (not target_address):
            raise ValueError("Target address not defined, in class or function")
        
        if code:
            data.set_data_code(code)

        self.socket.sendto(encode(data), target_address)

    def recv(self):
        try:
            new_data, address = self.socket.recvfrom(BUFFER_SIZE)

            return decode(new_data), address
        except:
            return None, None

    def send_recv(self, data:packet|None, code:int=None):
        self.send(data=data, code=code)
        new_data, _ = self.recv()

        return new_data

    def terminate(self):
        super().terminate()

        if (self.socket.fileno() != -1):
            self.socket.close()

    def get_new_instance(self):
        return thread_socket_wrapper(self.target, self.init, self.address, self.target_address, self.terminate_signal, self.name, self.sleep_time)

def encode(data:Any):
    return dumps(data).encode("utf-8")

def decode(data:bytes):
    return loads(data.decode("utf-8"))