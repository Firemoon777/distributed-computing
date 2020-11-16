from pa.ipc.communication_manager import CommunicationManager


class LamportMutex:
    """
    Класс решает вопросы взаимного исключения в распределённой системе с помощью алгоритма Лэмпорта.
    В нашей системе мютекс может быть только один, поэтому методы класса статичные.
    """

    @staticmethod
    def lock() -> None:
        """
        Пытаемся получить мютекс. Блокирующий вызов.
        :return: None
        """
        mgr = CommunicationManager()
        # Рассылаем всем предупреждение, что хотим в критическую секцию
        mgr.send_cs_request()
        # Ждём подтверждения от всех
        mgr.wait_for_acks()
        # Ждём наступления нашей очереди
        mgr.wait_for_queue()
        # Вход в КС выполнен

    @staticmethod
    def unlock():
        mgr = CommunicationManager()
        # Удаляемся из очереди
        mgr.send_cs_release()
