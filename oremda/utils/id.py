from oremda.typing import IdType
from typing import Optional
import uuid

def unique_id(id: Optional[IdType] = None) -> IdType:
    if id is None:
        return uuid.uuid4()
    else:
        return id

def port_id(node_id, port_name):
    return f'{node_id}/{port_name}'
