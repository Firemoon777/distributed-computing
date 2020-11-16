import os
import sys
import argparse
import time

from pa.ipc.communication_manager import CommunicationManager
from pa.ipc.logger import Logger
from pa.ipc.message import PARENT_ID


def parent_main(process_id: int, total_processes: int) -> int:
    # Инициализируем подключения всех процессов между собой
    c = CommunicationManager()
    c.connect_sockets(process_id, total_processes)

    c.receive_all_started()
    Logger.log_received_started(process_id)

    Logger.log_done(process_id)
    c.receive_all_done()
    Logger.log_received_done(process_id)

    # Родитель ожидает завершения всех детей прежде, чем завершится сам
    for i in range(1, total_processes):
        pid, exitcode = os.wait()
        assert exitcode == 0

    return 0


def child_main(process_id, total_processes) -> int:
    Logger.log_started(process_id, os.getpid(), os.getppid())
    # Инициализируем подключения всех процессов между собой
    c = CommunicationManager()
    c.connect_sockets(process_id, total_processes)

    c.send_started()
    c.receive_all_started()
    Logger.log_received_started(process_id)

    time.sleep(2)

    Logger.log_done(process_id)
    c.send_done()
    c.receive_all_done()
    Logger.log_received_done(process_id)

    return 0


def main() -> int:
    # Разбираем все аргументы стандартным способом
    parser = argparse.ArgumentParser(description='Runs distributed system with P separated processes with shared stdout')
    parser.add_argument('-p', help='Count of concurrent process', type=int)
    parser.add_argument('--mutexl', help='Enable mutual exclusion with Lamport''s algorithm', action='store_true')
    args = parser.parse_args(sys.argv[1:])

    total_processes = args.p + 1

    # Создаём P процессов, нумеруя с 1. Каждый процесс представляет собой самостоятельный узел распределённой системы.
    for i in range(1, total_processes):
        pid = os.fork()
        if pid == 0:
            # Этот код выполняется только ребёнком. После завершения полезной работы ребёнок должен завершиться.
            # Ребёнку необходимо знать свой идентификатор и общее количества процессов в системе.
            return child_main(i, total_processes)

    # После создания всех детей родитель приступает к собственной полезной нагрузке.
    # Идентификатор родителя определён заранее и равен PARENT_ID.
    return parent_main(PARENT_ID, total_processes)


if __name__ == '__main__':
    ret = main()
    # В явном виде указываем код возврата
    exit(ret)