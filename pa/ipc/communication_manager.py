from pa.handlers.acceptor import Acceptor
from pa.handlers.connector import Connector
from pa.reactor.event_type import EventType
from pa.reactor.reactor import Reactor

HOST = 'localhost'
BASE_PORT = 50000


class CommunicationManager:
    """
    Класс, представляющий общение всех процессов между собой. Он решает вопросы организации каналов связи
    между процессами и абстрагирует основную логику от реактора.
    """

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(CommunicationManager, cls).__new__(cls)
        return cls.instance

    def connect_sockets(self, process_id: int, total_processes: int) -> None:
        """
        Создает связи с каждым процессом в системе.
        :param process_id: идентификатор текущего процесса.
        :param total_processes: Число процессов в системе
        :return:
        """
        # Сначала создаём сокет, принимающий соединения. Из этого сокета мы будем получать сообщения от соседей
        listener = Acceptor(HOST, BASE_PORT + process_id)

        # Регистрируем его в реакторе
        r = Reactor()
        r.register_handler(listener, EventType.READ)

        # Запускаем процесс установления соединения с соседями, включая родителя
        for i in range(0, total_processes):
            r.handle_events(0.1)
            if i == process_id:
                continue
            # Пытаемся подключиться
            connected = False
            while not connected:
                try:
                    # Пытаемся подключиться
                    c = Connector(HOST, BASE_PORT + i)
                    connected = True
                    print(f'Process {process_id} connected to process {i}')
                except ConnectionRefusedError:
                    # Если возникает ошибка, то запускаем реактор одобрить чужие подключения
                    r.handle_events(0.1)

        # В конце могут остаться процессы, которые не успели соединиться. Даём им шанс.
        r.handle_events(1)