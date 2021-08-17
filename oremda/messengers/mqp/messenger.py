import json

import numpy as np

from oremda.messengers.base import BaseMessenger
from oremda.plasma_client import PlasmaArray

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

    def send(self, msg: dict, dest: str):
        msg = self.detach_data(msg)

        with open_queue(dest, create=True, reuse=True) as queue:
            queue.send(json.dumps(msg))

    def recv(self, source) -> dict:
        with open_queue(source, create=True, reuse=True, consume=True) as queue:
            msg, priority = queue.receive()

        msg = json.loads(msg)
        return self.join_data(msg)

    def detach_data(self, original_msg: dict):
        def recurse(cur, original_cur):
            for key, val in original_cur.items():
                if isinstance(val, PlasmaArray):
                    encoded = encode_data_key(key)
                    cur[encoded] = val.hex_id
                elif isinstance(val, np.ndarray):
                    encoded = encode_data_key(key)
                    array = PlasmaArray(self.plasma_client, val)
                    cur[encoded] = array.hex_id
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
                if is_encoded_key(key):
                    decoded = decode_data_key(key)
                    array = PlasmaArray(self.plasma_client, val)
                    cur[decoded] = array.data
                elif isinstance(val, dict):
                    cur[key] = {}
                    recurse(cur[key], val)
                else:
                    cur[key] = val

        msg = {}
        recurse(msg, original_msg)
        return msg


def encode_data_key(key: str) -> str:
    return f"data://{key}"


def is_encoded_key(key: str) -> bool:
    return key.startswith("data://")


def decode_data_key(key: str) -> str:
    prefix = "data://"
    start = len(prefix) if key.startswith(prefix) else 0
    return key[start:]
