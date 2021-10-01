import json

from oremda.messengers.base import BaseMessenger
from oremda.plasma_client import PlasmaArray
from oremda.typing import Message, Port

from .utils import open_queue


class MQPMessenger(BaseMessenger):
    """Message Queues and Plasma messenger

    Serializes a dict to json and sends it through the message queue. Any
    plasma arrays will have their object id sent instead of the array. Any
    numpy arrays will be placed in a plasma array, and the corresponding
    object id sent instead of the array. The receiver will replace any
    plasma object ids with their corresponding numpy arrays.

    The sender and receiver must be on the same node.
    """

    def __init__(self, plasma_client):
        self.plasma_client = plasma_client

    @property
    def type(self) -> str:
        return "mqp"

    def send(self, msg: Message, dest: str):
        serialized_msg = self.detach_data(dict(msg))

        with open_queue(dest, create=True, reuse=True) as queue:
            queue.send(json.dumps(serialized_msg))

    def recv(self, source) -> Message:
        with open_queue(source, create=True, reuse=True) as queue:
            serialized_msg, priority = queue.receive()

        serialized_msg = json.loads(serialized_msg)
        msg = self.join_data(serialized_msg)
        return Message(**msg)

    def detach_data(self, original_msg: dict):
        def recurse(cur, original_cur):
            for key, val in original_cur.items():
                if isinstance(val, Port):
                    encoded = encode_port_key(key)
                    serialized_port = {}
                    if val.meta is not None:
                        serialized_port["meta"] = val.meta
                    if isinstance(val.data, PlasmaArray):
                        serialized_port["data"] = val.data.hex_id
                    cur[encoded] = serialized_port
                elif isinstance(val, dict):
                    cur[key] = {}
                    recurse(cur[key], val)
                else:
                    cur[key] = val

        msg = {}
        recurse(msg, original_msg)
        return msg

    def join_data(self, original_msg: dict):
        def recurse(cur, original_cur):
            for key, val in original_cur.items():
                if is_port_key(key):
                    port = Port()
                    decoded = decode_port_key(key)
                    port.meta = val.get("meta")
                    data = val.get("data")
                    if data is not None:
                        port.data = PlasmaArray(self.plasma_client, data)

                    cur[decoded] = port
                elif isinstance(val, dict):
                    cur[key] = {}
                    recurse(cur[key], val)
                else:
                    cur[key] = val

        msg = {}
        recurse(msg, original_msg)
        return msg


PORT_PREFIX = "port://"


def encode_port_key(key: str) -> str:
    return f"{PORT_PREFIX}{key}"


def is_port_key(key: str) -> bool:
    return key.startswith(PORT_PREFIX)


def decode_port_key(key: str) -> str:
    start = len(PORT_PREFIX) if key.startswith(PORT_PREFIX) else 0
    return key[start:]
