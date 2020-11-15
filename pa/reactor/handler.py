from socket import socket


class EventHandler:
    """
    Абстрактный класс обработчика сообщений. При регистрации обработчика в реакторе указывается
    типы событий, которые будут обрабатываться конкретным экземляром.
    """

    def handle_input(self, handle: socket) -> None:
        """
        Вызывается, если обработчик зарегистрирован с EventType.READ
        """
        pass

    def handle_output(self, handle: socket) -> None:
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
