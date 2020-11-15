from socket import socket, AF_INET, SOCK_STREAM
from typing import Optional

from pa.reactor.handler import EventHandler


class Connector(EventHandler):
    """
    Connector на клиентской части позволяет подключиться к сокету и абстрагирует логику обработки сообщений
    от подключения к сокету.
    """

    _sock: socket
    _handler: EventHandler

    def __init__(self, host: str, port: int, handler: Optional[EventHandler] = None):
        # Сохраняем обработчик с логикой
        self._handler = handler

        # Инициализируем TCP-сокет
        self._sock = socket(AF_INET, SOCK_STREAM)

        # Выполняем подключение
        self._sock.connect((host, port))

    def __del__(self):
        self._sock.close()

    def handle_input(self, handle: socket) -> None:
        """
        Вызывается, если обработчик зарегистрирован с EventType.READ
        """
        print('input')
        if self._handler is not None:
            self._handler.handle_input(handle)

    def handle_output(self, handle: socket) -> None:
        """
        Вызывается, если обработчик зарегистрирован с EventType.WRITE
        """
        if self._handler is not None:
            self._handler.handle_output(handle)

    def get_handle(self) -> socket:
        """
        Возвращает объект, события с которым хочется обрабатывать.
        По условию лаборатнорной работы это сокеты, поэтому тип указан строго сокет.
        """
        return self._sock