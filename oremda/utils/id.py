import uuid

def unique_id(id=None):
    if id is None:
        return uuid.uuid4()
    else:
        return id

def port_id(node_id, port_name):
    return f'{node_id}/{port_name}'
