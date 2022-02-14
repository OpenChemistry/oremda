from uuid import UUID
from fastapi_websocket_rpc.simplewebsocket import SimpleWebSocket

import msgpack
from pydantic import BaseModel


ENCODERS_BY_TYPE = {
    UUID: str,
}


def default(obj):
    if isinstance(obj, BaseModel):
        return obj.dict()

    encoder = ENCODERS_BY_TYPE.get(type(obj))
    if encoder:
        return encoder(obj)
    return obj


class MsgpackSerializingWebSocket(SimpleWebSocket):
    def __init__(self, websocket) -> None:
        super().__init__()
        self._websocket = websocket

    def _serialize(self, msg):
        return msgpack.packb(msg, default=default)

    def _deserialize(self, buffer):
        return msgpack.unpackb(buffer)

    async def send(self, msg):
        await self._websocket.send(self._serialize(msg))

    async def recv(self):
        msg = await self._websocket.recv()

        return self._deserialize(msg)

    async def close(self, code: int = 1000):
        await self._websocket.close(code)
