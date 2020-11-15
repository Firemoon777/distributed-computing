import os
import sys
import argparse

from pa.ipc.message import PARENT_ID


def parent_main(parent_id: int, total_processes: int) -> int:
    pass


def child_main(child_id, total_processes) -> int:
    pass


def main() -> int:
    # Разбираем все аргументы стандартным способом
    parser = argparse.ArgumentParser(description='Runs distributed system with P separated processes with shared stdout')
    parser.add_argument('-p', help='Count of concurrent process', type=int)
    parser.add_argument('--mutexl', help='Enable mutual exclusion with Lamport''s algorithm', action='store_true')
    args = parser.parse_args(sys.argv[1:])

    # Создаём P процессов, нумеруя с 1. Каждый процесс представляет собой самостоятельный узел распределённой системы.
    for i in range(1, args.p + 1):
        pid = os.fork()
        if pid == 0:
            # Этот код выполняется только ребёнком. После завершения полезной работы ребёнок должен завершиться.
            # Ребёнку необходимо знать свой идентификатор и общее количества процессов в системе.
            return child_main(i, args.P)

    # После создания всех детей родитель приступает к собственной полезной нагрузке.
    # Идентификатор родителя определён заранее и равен PARENT_ID.
    return parent_main(PARENT_ID, args.P)


if __name__ == '__main__':
    from pa.reactor.reactor import Reactor
    r = Reactor()

    from pa.handlers.connector import Connector
    h = Connector('127.0.0.1', 30000)

    from pa.reactor.event_type import EventType
    r.register_handler(h, EventType.READ | EventType.WRITE)

    r.handle_events(2)

    #ret = main()
    # В явном виде указываем код возврата
    # exit(ret)