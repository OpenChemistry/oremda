DEFAULT_OREMDA_VAR_DIR = '/run/oremda'
DEFAULT_PLASMA_SOCKET_PATH = f'{DEFAULT_OREMDA_VAR_DIR}/plasma.sock'
DEFAULT_DATA_DIR = '/data'

OREMDA_FINISHED_QUEUE = '/oremda_finished_queue'

class NodeType:
    Operator = 'operator'

class PortType:
    Data = 'data'
    Meta = 'meta'

class IOType:
    In = 'in'
    Out = 'out'

class TaskType:
    Operate = 'operate'
    Terminate = 'terminate'
