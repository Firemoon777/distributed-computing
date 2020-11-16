import sys
import time
from random import random


def concurrent_print(s: str, f=sys.stdout) -> None:
    """
    Печатает строку посимвольно с небольшими псевдослучаныйми задержками между символами.
    :param s: строка
    :param f: файл
    :return: None
    """
    for c in s:
        time.sleep(random() / 100)
        print(c, end='', file=f, flush=True)


def lab_print(process_id: int, it: int, total:int) -> None:
    s = f'process {process_id:3d} is doing {it} iteration out of {total}\n'
    concurrent_print(s)