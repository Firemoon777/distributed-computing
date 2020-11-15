from enum import IntEnum
import struct

PARENT_ID = 0
MAX_PROCESS_ID = 100
MAX_MESSAGE_LEN = 4096
MESSAGE_MAGIC = 0xAFAF


class MessageType(IntEnum):
    STARTED = 1,
    DONE = 2,
    CS_REQUEST = 3,
    CS_REPLY = 4,
    CS_RELEASE = 5


class Message:
    magic: int
    message_type: MessageType
    local_time: int
    payload_len: int
    payload: bytes

    def __init__(self, msg_type: MessageType, local_time: int, payload=b''):
        self.magic = MESSAGE_MAGIC
        self.message_type = msg_type
        self.local_time = local_time
        self.payload = payload
        self.payload_len = len(self.payload)

    @staticmethod
    def from_bytes(msg: bytes) -> 'Message':
        header = msg[:10]
        payload = msg[10:]

        magic, type, local_time, payload_len = struct.unpack('>HHIH', header)
        assert magic == MESSAGE_MAGIC
        return Message(type, local_time, payload)

    def to_bytes(self) -> bytes:
        fmt = f'>HHIH{self.payload_len}s'
        return struct.pack(fmt, self.magic, self.message_type, self.local_time, self.payload_len, self.payload)

