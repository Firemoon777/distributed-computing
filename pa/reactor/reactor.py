import time
from select import select
from socket import socket

from pa.reactor.event_type import EventType
from pa.reactor.handler import EventHandler


class Reactor:
    """
    Главная часть реактора. Здесь происходит регистрация и удаление зарегистрированных обработчиков,
    здесь происходит магия по запуску обработчиков. Реактор представлен синглтоном.
    """

    # Ассоциативный массив "сокет-массив обработчиков"
    _handler_map = {}

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Reactor, cls).__new__(cls)
        return cls.instance

    def register_handler(self, handler: EventHandler, event_type: EventType, handle: socket = None) -> None:
        """
        Добавляет обработчик событий в реактор
        :param handler: обработчик
        :param event_type: события на которые необходимо уведомлять обработчик
        :param handle: сокет, события которого хотим обрабатывать. Если None, то берется из обработчика.
        :return: None
        """
        if handle is None:
            handle = handler.get_handle()

        # Если в нашем словаре нет такой записи, то создаём
        if handle not in self._handler_map:
            self._handler_map[handle] = []

        # Создаёем и добавляем запись в словарь
        entry = {
            'handler': handler,
            'event_type': event_type
        }
        self._handler_map[handle].append(entry)

    def remove_handler(self, handler: EventHandler, event_type: EventType, handle: socket = None) -> None:
        """
        Удаляет обработчик по информации о нём. Удаляется только при полном совпадении.
        :param handler: обработчик, который нужно удалить
        :param event_type: виды событий, на которые реагирует обработчик
        :param handle: сокет. Если None, то берется из обработчика
        :return: None
        """
        if handle is None:
            handle = handler.get_handle()

        # Если в нашем словаре нет такой записи, то выходим
        if handle not in self._handler_map:
            return

        # Если есть что удалять -- удаляем
        for entry in self._handler_map[handle]:
            if entry.handler == handler and entry.event_type == event_type:
                self._handler_map[handle].remove(entry)

    def handle_events(self, timeout) -> None:
        """
        Главный цикл реактора. Работает в течение timeout секунд. Использует select, поддерживаемый на всех
        операционных системах, включая Windows.
        :param timeout: время в секундах, в течение которого реактор будет ждать событий на сокетах
        :return: None
        """
        # Запоминаем время начала
        start = time.time()

        # Пока есть время -- выполняем цикл реактора
        while time.time() - start < timeout:
            # Создаём два списка: в одном сокеты, за которыми следим за чтением, а в другом -- на запись
            read_list = []
            write_list = []

            # Заполняем списки
            for key in self._handler_map.keys():
                for entry in self._handler_map[key]:
                    if entry['event_type'] & EventType.READ.value:
                        read_list.append(key)
                    if entry['event_type'] & EventType.WRITE.value:
                        write_list.append(key)

            # Вычисляем таймаут для select, чтобы не выйти за предел времени реактора.
            # Время select ограничено сверху одной секундой на случай появления новых сокетов и обработчиков.
            select_timeout = min(timeout - (time.time() - start), 1)
            if select_timeout < 0:
                return

            # Запускаем select с таймаутом
            readable, writable, errored = select(read_list, write_list, [], select_timeout)

            # Проходим по всем сокетам, которые готовы к чтению
            for s in readable:
                # Передаем вопросы работы с этим сокетам соответствующим обработчикам
                for entry in self._handler_map[s]:
                    if entry['event_type'] & EventType.READ.value:
                        entry['handler'].handle_input(s)

            # Проходим по всем сокетам, которые готовы к записи
            for s in writable:
                # Передаем вопросы работы с этим сокетам соответствующим обработчикам
                for entry in self._handler_map[s]:
                    if entry['event_type'] & EventType.WRITE.value:
                        entry['handler'].handle_output(s)