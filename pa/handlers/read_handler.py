from socket import socket
from typing import Optional

from pa.ipc.message import Message, MessageType
from pa.lamport.time import LamportTime
from pa.reactor.handler import EventHandler


class ReadHandler(EventHandler):

    started: int
    done: int
    _process_id: int

    def __init__(self, process_id: int):
        self._process_id = process_id
        self.started = 1
        self.done = 1
        if self._process_id != 0:
            self.started += 1
            self.done += 1

    def handle_input(self, handle: socket) -> None:
        m = Message.from_socket(handle)
        t = LamportTime().inc_time(m.local_time)
        if m.message_type == MessageType.STARTED:
            self.started += 1
        elif m.message_type == MessageType.DONE:
            self.done += 1

    def handle_output(self, handle: socket) -> None:
        super().handle_output(handle)

    def get_handle(self) -> socket:
        return super().get_handle()