from socket import socket
from typing import Optional

from pa.ipc.message import Message, MessageType
from pa.lamport.time import LamportTime
from pa.reactor.event_type import EventType
from pa.reactor.handler import EventHandler
from pa.reactor.reactor import Reactor


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

    def handle_input(self, handle: socket) -> int:
        """
        Обрабатываем чтение. Если прочитали хоть что-то, то возвращаем 0. Если прочитали 0 байт, то возвращаем 1,
        чтобы уведомить Acceptor о том, что из сокета уже ничего не читается и его надо закрыть
        :param handle: сокет
        :return: 0, если всё ок, 1, если нужно закрыть сокет
        """
        m = Message.from_socket(handle)
        # Ничего не прочиталось
        if m.message_type is None:
            return 1

        # Обновляем время Лэмпорта
        LamportTime().inc_time(m.local_time)

        print(f'Process {self._process_id} gets Message {m.message_type} from process {m.src_id}')

        # Проводим обработку сообщений
        if m.message_type == MessageType.STARTED:
            self.started += 1
        elif m.message_type == MessageType.DONE:
            self.done += 1

        return 0

    def handle_output(self, handle: socket) -> None:
        super().handle_output(handle)

    def get_handle(self) -> socket:
        return super().get_handle()