from enum import IntEnum


class EventType(IntEnum):
    READ = 0b01,
    WRITE = 0b10
