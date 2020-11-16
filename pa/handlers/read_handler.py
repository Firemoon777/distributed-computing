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

    ack: int
    queue: list

    def __init__(self, process_id: int):
        self._process_id = process_id
        self.started = 1
        self.done = 1
        if self._process_id != 0:
            self.started += 1
            self.done += 1

        self.ack = 1
        self.queue = list()

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

        # print(f'Process {self._process_id} gets Message {m.message_type} from process {m.src_id}')

        # Проводим обработку сообщений
        if m.message_type == MessageType.STARTED:
            # Кто-то запустился. Увеличиваем счётчик
            self.started += 1
        elif m.message_type == MessageType.DONE:
            # Кто-то завершил полезную работу. Увеличиваем счётчик.
            self.done += 1
        elif m.message_type == MessageType.CS_REQUEST:
            # Кто-то запрашивает право зайти в критическую секцию.
            # Добавляем запись в свою очередь вида (время; идентификатор)
            self.queue.append((m.local_time, m.src_id))
            # Сортируем по времени
            self.queue.sort()
            # Так как у нас связи с менеджером, но нам очень хочется отправить сообщение,
            # то для избежания циклической зависимости делаем импорт локальным
            from pa.ipc.communication_manager import CommunicationManager
            # Отправляем сообщение-подтверждение
            mgr = CommunicationManager()
            mgr.send_cs_reply(m.src_id)
        elif m.message_type == MessageType.CS_REPLY:
            # Кто-то записал нашу просьбу о входе в КС. Увеличиваем счётчик.
            self.ack += 1
        elif m.message_type == MessageType.CS_RELEASE:
            # Процесс вышел из КС и просит нас удалить его из очереди
            for entry in self.queue:
                if entry[1] == m.src_id:
                    self.queue.remove(entry)
                    break
        return 0

    def handle_output(self, handle: socket) -> None:
        super().handle_output(handle)

    def get_handle(self) -> socket:
        return super().get_handle()