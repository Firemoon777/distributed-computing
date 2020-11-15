from socket import socket

from pa.reactor.handler import EventHandler


class Connector(EventHandler):
    """

    """

    def handle_input(self) -> None:
        """
        Вызывается, если обработчик зарегистрирован с EventType.READ
        """
        pass

    def handle_output(self) -> None:
        """
        Вызывается, если обработчик зарегистрирован с EventType.WRITE
        """
        pass

    def get_handle(self) -> socket:
        """
        Возвращает объект, события с которым хочется обрабатывать.
        По условию лаборатнорной работы это сокеты, поэтому тип указан строго сокет.
        """
        pass