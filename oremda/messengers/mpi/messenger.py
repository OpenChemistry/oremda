from mpi4py import MPI
from pydantic import validate_arguments

from oremda.constants import DEFAULT_PLASMA_SOCKET_PATH
from oremda.messengers.base import BaseMessenger
from oremda.plasma_client import PlasmaArray, PlasmaClient
from oremda.typing import Message, Port

comm = MPI.COMM_WORLD
rank = comm.Get_rank()


class MPIMessenger(BaseMessenger):
    """Message Passing Interface messenger

    Sends a whole dict through MPI via pickling.

    The sender and receiver can be on different nodes.
    """

    def __init__(self):
        self.plasma_client = PlasmaClient(DEFAULT_PLASMA_SOCKET_PATH)

    @property
    def type(self) -> str:
        return "mpi"

    @validate_arguments
    def send(self, msg: Message, dest: int):
        msg = self.detach_data(dict(msg))
        comm.send(msg, dest=dest)

    @validate_arguments
    def recv(self, source: int) -> Message:
        msg = comm.recv(source=source)
        msg = self.join_data(msg)
        return Message(**msg)

    def detach_data(self, original_msg: dict):
        # Recurse through the message and convert any Plasma arrays to numpy
        # This does not actually detach the data, but is named this to match
        # the naming conventions for MQP.
        def recurse(cur, original_cur):
            for key, val in original_cur.items():
                if isinstance(val, Port):
                    encoded = encode_port_key(key)
                    serialized_port = {}
                    if val.meta is not None:
                        serialized_port["meta"] = val.meta
                    if isinstance(val.data, PlasmaArray):
                        serialized_port["data"] = val.data.data
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
