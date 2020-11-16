from socket import socket, SOCK_STREAM, AF_INET, SO_REUSEADDR, SOL_SOCKET
from typing import Optional

from pa.reactor.event_type import EventType
from pa.reactor.handler import EventHandler
from pa.reactor.reactor import Reactor


class Acceptor(EventHandler):
    """
    Acceptor позволяет абстрагировать инициализацию сокета от логики обработки события.
    """

    _sock: socket
    _handler: EventHandler
    _client: list

    def __init__(self, host: str, port: int, handler: Optional[EventHandler] = None):
        """
        Инициализируем сокет и настраиваем прокси для следующего обработчика
        :param handler: обработчик событий для сокета
        """

        # Создаём массив для клиентских сокетов
        self._client = list()

        # Сохраняем обработчик с логикой
        self._handler = handler

        # Инициализируем TCP-сокет
        self._sock = socket(AF_INET, SOCK_STREAM)

        # Так как инициатива закрытия сокета может быть на сервере, добавляем флаг REUSEADDR
        # Это позволит избежать ошибки "Address already in use" при перезапуске системы
        self._sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

        # Привязываем его к адресу и порту
        self._sock.bind((host, port))

        # Открываем сокет. Заранее ставим большой бэклог подключений для большой системы
        self._sock.listen(1000)

    def __del__(self):
        for sock in self._client:
            sock.close()
        self._sock.close()

    def handle_input(self, handle: socket) -> None:
        """
        Вызывается, если обработчик зарегистрирован с EventType.READ
        """
        # Особенность слушающих сокетов в том, что на "оригинальном" сокете операция чтения
        # эквивалентна входящему запросу на подключение, поэтому проверяем, является ли сокет "оригинальным"
        if handle == self._sock:
            # Это подключение, необходимо его принять
            client, address = self._sock.accept()
            # Теперь у нас есть сокет, который связывает нас с конкертным клиентом.
            # Регистрируем себя в реакторе для нового сокета.
            r = Reactor()
            r.register_handler(self, EventType.READ, client)
            # Сохраняем сокет себе, чтобы закрыть его, когда придёт время
            self._client.append(client)
            # События ACCEPT мы не прокидываем дальше, так что завершаемся
            return

        if self._handler is not None:
            ret = self._handler.handle_input(handle)
            if ret == 1:
                # Вложенный обработчик сообщает, что из сокета ничего не прочитать. Отписываемся от
                # наблюдения в реакторе и закрываем сокет
                r = Reactor()
                r.remove_handler(self, EventType.READ, handle)

                handle.close()

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