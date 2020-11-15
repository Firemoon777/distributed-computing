from socket import socket

from pa.ipc.message import Message
from pa.reactor.handler import EventHandler


class WriteHandler(EventHandler):
    """
    Обработчик, принимающий сообщения на запись
    """

    _queue: list

    def __init__(self):
        self._queue = list()

    def add(self, msg: Message) -> None:
        """
        Добавляет сообщение в очередь отправки
        :param msg: сообщение
        :return:
        """
        self._queue.append(msg)

    def handle_input(self, handle: socket) -> None:
        """
        В данном обработчике игноируется
        :param handle:
        :return:
        """
        super().handle_input(handle)

    def handle_output(self, handle: socket) -> None:
        """
        Проверяет очередь и отправляет одно сообщение
        :param handle: сокет
        :return:
        """
        if len(self._queue) == 0:
            return
        m = self._queue.pop(0)
        handle.send(m.to_bytes())

    def get_handle(self) -> socket:
        return super().get_handle()
