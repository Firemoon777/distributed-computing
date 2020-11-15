from pa.ipc.message import Message, MessageType, MESSAGE_MAGIC


def test_empty_message():
    m = Message(MessageType.CS_REQUEST, 5)
    assert m.magic == MESSAGE_MAGIC
    assert m.payload_len == 0

    byte_message = m.to_bytes()
    assert byte_message == b'\xaf\xaf\x00\x03\x00\x00\x00\x05\x00\x00'

    recv = Message.from_bytes(byte_message)
    assert recv.message_type == MessageType.CS_REQUEST
    assert recv.local_time == 5


def test_message_with_payload():
    payload = b'STARTED'
    m = Message(MessageType.STARTED, 1, payload)

    assert m.magic == MESSAGE_MAGIC
    assert m.payload_len == len(payload)
    assert m.payload == payload

    byte_message = m.to_bytes()
    assert byte_message == b'\xaf\xaf\x00\x01\x00\x00\x00\x01\x00\x07STARTED'

    recv = Message.from_bytes(byte_message)
    assert recv.payload_len == len(payload)
    assert recv.payload == payload
