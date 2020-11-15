import time

from pa.handlers.acceptor import Acceptor
from pa.handlers.connector import Connector
from pa.handlers.read_handler import ReadHandler
from pa.handlers.write_handler import WriteHandler
from pa.ipc.message import Message, MessageType
from pa.lamport.time import LamportTime
from pa.reactor.event_type import EventType
from pa.reactor.reactor import Reactor

HOST = 'localhost'
BASE_PORT = 50030


class CommunicationManager:
    """
    Класс, представляющий общение всех процессов между собой. Он решает вопросы организации каналов связи
    между процессами и абстрагирует основную логику от реактора.
    """

    _handlers: dict
    _process_id: int
    _total_processes: int

    def __init__(self):
        self._handlers = dict()

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
        # Сохраняем значения
        self._process_id = process_id
        self._total_processes = total_processes

        # Сначала создаём сокет, принимающий соединения. Из этого сокета мы будем получать сообщения от соседей
        read_handler = ReadHandler(process_id)
        listener = Acceptor(HOST, BASE_PORT + process_id, read_handler)

        # Регистрируем его в реакторе
        r = Reactor()
        r.register_handler(listener, EventType.READ)

        # Запускаем процесс установления соединения с соседями, включая родителя
        for i in range(0, total_processes):
            r.handle_events(0.1)
            if i == process_id:
                self._handlers[i] = read_handler
                continue
            # Пытаемся подключиться
            connected = False
            while not connected:
                try:
                    w = WriteHandler()
                    # Пытаемся подключиться
                    c = Connector(HOST, BASE_PORT + i, w)
                    # Раз нет исключения, то мы подключились, регистрируем коннектор в реакторе
                    r.register_handler(c, EventType.WRITE)
                    # Сохраняем себе копию WriteHandler'а
                    self._handlers[i] = w
                    # Выходим из цикла
                    connected = True
                except ConnectionRefusedError:
                    # Если возникает ошибка, то запускаем реактор одобрить чужие подключения
                    r.handle_events(0.1)

        # В конце могут остаться процессы, которые не успели соединиться. Даём им шанс. Хотя это не обязательно.
        r.handle_events(1)

    def send(self, dst: int, msg: Message) -> None:
        """
        Ставит сообщение в очередь отправки для конкретного адресата. Выставляет для сообщения
        корректное время Лэмпорта
        :param dst: кому отправляем сообщение
        :param msg: сообщение
        :return: None
        """
        msg.local_time = LamportTime().inc_time()
        self._handlers[dst].add(msg)

    def broadcast(self, msg: Message) -> None:
        """
        Ставит сообщегие в очередь отправки для всех, кроме себя. Выставляет для сообщения корректное время Лэмпорта
        :param msg:
        :return:
        """
        msg.local_time = LamportTime().inc_time()
        for i in range(0, self._total_processes):
            if i == self._process_id:
                continue
            self._handlers[i].add(msg)

    def send_started(self) -> None:
        m = Message(MessageType.STARTED)
        self.broadcast(m)

    def receive_all_started(self) -> None:
        r = Reactor()
        while self._handlers[self._process_id].started != self._total_processes:
            r.handle_events(0.1)

    def send_done(self) -> None:
        m = Message(MessageType.DONE)
        self.broadcast(m)

    def receive_all_done(self) -> None:
        r = Reactor()
        while self._handlers[self._process_id].done != self._total_processes:
            r.handle_events(0.1)
        r.handle_events(5)
