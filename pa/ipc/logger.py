import sys

from pa.lamport.time import LamportTime


class Logger:
    """
    Логгирует в stdout
    """

    @staticmethod
    def log_started(id: int, pid: int, ppid: int):
        lamport = LamportTime()
        timestamp = lamport.get_time()
        print(f'{timestamp}: process {id:2d} (pid {pid:6d}, parent {ppid:6d}) has STARTED')
        sys.stdout.flush()

    @staticmethod
    def log_received_started(id: int):
        lamport = LamportTime()
        timestamp = lamport.get_time()
        print(f'{timestamp}: process {id:2d} received all STARTED messages')
        sys.stdout.flush()

    @staticmethod
    def log_done(id: int):
        lamport = LamportTime()
        timestamp = lamport.get_time()
        print(f'{timestamp}: process {id:2d} has DONE')
        sys.stdout.flush()

    @staticmethod
    def log_received_done(id: int):
        lamport = LamportTime()
        timestamp = lamport.get_time()
        print(f'{timestamp}: process {id:2d} received all DONE messages')
        sys.stdout.flush()