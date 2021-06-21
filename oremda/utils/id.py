import uuid

def unique_id(id=None):
    if id is None:
        return uuid.uuid4()
    else:
        return id
