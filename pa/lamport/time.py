class LamportTime:
    """
    Класс представляет счётчик скалярного времени Лэмпорта
    """

    _clock = 1

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(LamportTime, cls).__new__(cls)
        return cls.instance

    def get_time(self) -> int:
        """
        :return: Возвращает текущее скалярное время процесса
        """
        return self._clock

    def update_time(self, time: int) -> int:
        """
        Обновляет время Лэмпорта, если метка времени другого процесса больше
        :param time: метка времени другого процесса
        :return: новое время Лэмпорта
        """
        if time > self._clock:
            self._clock = time
        return self._clock

    def inc_time(self, time: int = 0) -> int:
        """
        Обновляет, если необходимо время Лэмпорта, а затем увеличивает на единицу
        :param time: метка времени другого процесса
        :return: новое время лэмпорта
        """
        self.update_time(time)
        self._clock = self._clock + 1
        return self._clock
