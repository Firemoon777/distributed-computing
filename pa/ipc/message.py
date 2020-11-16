from enum import IntEnum, unique
import struct
from socket import socket

PARENT_ID = 0
MAX_PROCESS_ID = 100
MAX_MESSAGE_LEN = 4096
MESSAGE_MAGIC = 0xAFAF


@unique
class MessageType(IntEnum):
    STARTED = 1,
    DONE = 2,
    CS_REQUEST = 3,
    CS_REPLY = 4,
    CS_RELEASE = 5


class Message:
    """
    Класс, представляющий сообщение, которыми обмениваются процессы распределённой системы.
    """
    magic: int
    message_type: MessageType
    src_id: int
    local_time: int
    payload_len: int
    payload: bytes

    def __init__(self, msg_type: MessageType, src_id: int, local_time=0, payload=b''):
        self.magic = MESSAGE_MAGIC
        self.message_type = msg_type
        self.src_id = src_id
        self.local_time = local_time
        self.payload = payload
        self.payload_len = len(self.payload)

    @staticmethod
    def from_bytes(msg: bytes) -> 'Message':
        """
        Создаёт сообщение из массива байт
        :param msg: байты сообщения
        :return: экземпляр класса Message
        """
        header = msg[:12]
        payload = msg[12:]

        magic, type, src, local_time, payload_len = struct.unpack('>HHHIH', header)
        assert magic == MESSAGE_MAGIC
        return Message(type, src, local_time, payload)

    @staticmethod
    def from_socket(handle: socket) -> 'Message':
        """
        Считывает сообщение прямиком из сокета
        :param handle: сокет
        :return: сообщение
        """
        header = handle.recv(12)
        if len(header) == 0:
            return Message(None, -1)
        payload = b''
        magic, type, src_id, local_time, payload_len = struct.unpack('>HHHIH', header)
        assert magic == MESSAGE_MAGIC
        if payload_len != 0:
            payload = handle.recv(payload_len)
        return Message(type, src_id, local_time, payload)

    def to_bytes(self) -> bytes:
        """
        Конвертирует сообщение в массив байт, пригодных для отправки
        :return: массив байт
        """
        fmt = f'>HHHIH{self.payload_len}s'
        return struct.pack(fmt, self.magic, self.message_type, self.src_id, self.local_time, self.payload_len, self.payload)

